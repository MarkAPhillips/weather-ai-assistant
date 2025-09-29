import requests
from typing import Dict, List, Optional
from datetime import datetime, timezone
import logging
from models.air_quality import AirQualityData

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AirQualityService:
    """Air quality service using OpenWeatherMap Air Pollution API."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/air_pollution"
        self.cache = {}
        self.cache_duration = 600  # 10 minutes (air quality changes slower)

    def _is_cache_valid(self, city_key: str) -> bool:
        """Check if cached air quality data is still valid."""
        if city_key not in self.cache:
            return False

        cache_time = self.cache[city_key]["timestamp"]
        return (datetime.now(timezone.utc) - cache_time).seconds < \
            self.cache_duration

    def _get_aqi_from_pollutants(self, pollutants: Dict[str, float]) -> int:
        """Calculate AQI from pollutant concentrations (US EPA standard)."""
        # Use PM2.5 as primary indicator for AQI calculation
        pm25 = pollutants.get('pm25', 0)

        if pm25 <= 12.0:
            return int((pm25 / 12.0) * 50)
        elif pm25 <= 35.4:
            return int(((pm25 - 12.1) / (35.4 - 12.1)) * (100 - 51) + 51)
        elif pm25 <= 55.4:
            return int(((pm25 - 35.5) / (55.4 - 35.5)) * (150 - 101) + 101)
        elif pm25 <= 150.4:
            return int(((pm25 - 55.5) / (150.4 - 55.5)) * (200 - 151) + 151)
        elif pm25 <= 250.4:
            return int(((pm25 - 150.5) / (250.4 - 150.5)) * (300 - 201) + 201)
        elif pm25 <= 350.4:
            return int(((pm25 - 250.5) / (350.4 - 250.5)) * (400 - 301) + 301)
        elif pm25 <= 500.4:
            return int(((pm25 - 350.5) / (500.4 - 350.5)) * (500 - 401) + 401)
        else:
            return 500

    def _get_health_recommendations(self, aqi: int) -> List[str]:
        """Get health recommendations based on AQI."""
        if aqi <= 50:
            return [
                "Air quality is good - suitable for outdoor activities",
                "No health impacts expected for the general population"
            ]
        elif aqi <= 100:
            return [
                "Air quality is moderate - acceptable for most people",
                "Sensitive individuals may experience minor breathing issues"
            ]
        elif aqi <= 150:
            return [
                "Air quality is unhealthy for sensitive groups",
                "Children, elderly, and people with heart/lung disease "
                "should limit outdoor activities",
                "Consider wearing a mask if you're sensitive to pollution"
            ]
        elif aqi <= 200:
            return [
                "Air quality is unhealthy - everyone may experience effects",
                "Sensitive groups should avoid outdoor activities",
                "General population should limit prolonged outdoor exertion"
            ]
        elif aqi <= 300:
            return [
                "Air quality is very unhealthy",
                "Everyone should avoid outdoor activities",
                "Stay indoors with windows closed if possible"
            ]
        else:
            return [
                "Air quality is hazardous",
                "Everyone should stay indoors",
                "Avoid all outdoor activities",
                "Consider using air purifiers indoors"
            ]

    def get_air_quality_data(self, city: str,
                             country: str = None) -> Optional[AirQualityData]:
        """Get air quality data for a city using coordinates."""
        cache_key = f"{city}_{country}" if country else city

        # Check cache first
        if self._is_cache_valid(cache_key):
            logger.info(f"Using cached air quality data for {cache_key}")
            return self.cache[cache_key]["data"]

        try:
            # First, get coordinates from OpenWeatherMap geocoding API
            geocoding_url = "http://api.openweathermap.org/geo/1.0/direct"
            geocoding_params = {
                "q": f"{city},{country}" if country else city,
                "limit": 1,
                "appid": self.api_key
            }

            geocoding_response = requests.get(
                geocoding_url, params=geocoding_params, timeout=10
            )
            geocoding_response.raise_for_status()

            geocoding_data = geocoding_response.json()
            if not geocoding_data:
                logger.warning(f"No coordinates found for {city}")
                return None

            lat = geocoding_data[0]["lat"]
            lon = geocoding_data[0]["lon"]

            # Now get air pollution data using coordinates
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key
            }

            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if not data.get("list") or len(data["list"]) == 0:
                logger.warning(f"No air quality data found for {city}")
                return None

            # Extract air pollution data
            pollution_data = data["list"][0]["components"]

            # Extract pollutants
            pm25 = pollution_data.get("pm2_5")
            pm10 = pollution_data.get("pm10")
            o3 = pollution_data.get("o3")
            no2 = pollution_data.get("no2")
            so2 = pollution_data.get("so2")
            co = pollution_data.get("co")

            # Calculate AQI from pollutants
            pollutants_dict = {
                'pm25': pm25,
                'pm10': pm10,
                'o3': o3,
                'no2': no2,
                'so2': so2,
                'co': co
            }

            aqi = self._get_aqi_from_pollutants(pollutants_dict)

            # Get health recommendations
            health_recommendations = self._get_health_recommendations(aqi)

            air_quality_data = AirQualityData(
                aqi=aqi,
                pm25=pm25,
                pm10=pm10,
                o3=o3,
                no2=no2,
                so2=so2,
                co=co,
                location=f"{city}, {country}" if country else city,
                timestamp=datetime.now(timezone.utc).isoformat(),
                health_recommendations=health_recommendations
            )

            # Cache the result
            self.cache[cache_key] = {
                "data": air_quality_data,
                "timestamp": datetime.now(timezone.utc)
            }

            logger.info(f"Successfully fetched air quality data for {city}")
            return air_quality_data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching air quality data for {city}: {e}")
            return None
        except Exception as e:
            logger.error(
                f"Unexpected error fetching air quality data for {city}: {e}"
            )
            return None

    def get_air_quality_summary(self, air_quality: AirQualityData) -> str:
        """Generate a human-readable air quality summary."""
        if not air_quality or not air_quality.aqi:
            return "Air quality data not available"

        aqi = air_quality.aqi

        if aqi <= 50:
            status = "Good"
            color = "🟢"
        elif aqi <= 100:
            status = "Moderate"
            color = "🟡"
        elif aqi <= 150:
            status = "Unhealthy for Sensitive Groups"
            color = "🟠"
        elif aqi <= 200:
            status = "Unhealthy"
            color = "🔴"
        elif aqi <= 300:
            status = "Very Unhealthy"
            color = "🟣"
        else:
            status = "Hazardous"
            color = "🟤"

        summary = f"{color} Air Quality Index: {aqi} ({status})"

        if air_quality.pm25:
            summary += f"\nPM2.5: {air_quality.pm25:.1f} μg/m³"

        if air_quality.pm10:
            summary += f"\nPM10: {air_quality.pm10:.1f} μg/m³"

        return summary
