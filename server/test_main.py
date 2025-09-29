"""
Basic test file for the weather AI assistant API.
This file contains tests for the main application and services.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone

# Import the services and models
from services.air_quality_service import AirQualityService
from models.air_quality import AirQualityData


class TestAirQualityService:
    """Test cases for the AirQualityService class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.api_key = "test_api_key"
        self.service = AirQualityService(self.api_key)

    def test_air_quality_service_initialization(self):
        """Test that AirQualityService initializes correctly."""
        assert self.service.api_key == "test_api_key"
        assert self.service.base_url == "http://api.openweathermap.org/data/2.5/air_pollution"
        assert self.service.cache == {}
        assert self.service.cache_duration == 600

    def test_cache_validation_empty_cache(self):
        """Test cache validation when cache is empty."""
        city_key = "london_gb"
        assert not self.service._is_cache_valid(city_key)

    def test_cache_validation_valid_cache(self):
        """Test cache validation with valid cached data."""
        city_key = "london_gb"
        # Add valid cache entry
        self.service.cache[city_key] = {
            "data": {"aqi": 50},
            "timestamp": datetime.now(timezone.utc)
        }
        assert self.service._is_cache_valid(city_key)

    def test_cache_validation_expired_cache(self):
        """Test cache validation with expired cached data."""
        city_key = "london_gb"
        # Add expired cache entry (older than 10 minutes)
        from datetime import timedelta
        old_time = datetime.now(timezone.utc) - timedelta(minutes=11)
        self.service.cache[city_key] = {
            "data": {"aqi": 50},
            "timestamp": old_time
        }
        assert not self.service._is_cache_valid(city_key)

    def test_aqi_calculation_good_air_quality(self):
        """Test AQI calculation for good air quality (PM2.5 <= 12)."""
        pollutants = {"pm25": 8.0}
        aqi = self.service._get_aqi_from_pollutants(pollutants)
        assert aqi == 33  # (8.0 / 12.0) * 50

    def test_aqi_calculation_moderate_air_quality(self):
        """Test AQI calculation for moderate air quality (PM2.5 12.1-35.4)."""
        pollutants = {"pm25": 20.0}
        aqi = self.service._get_aqi_from_pollutants(pollutants)
        assert 51 <= aqi <= 100

    def test_aqi_calculation_unhealthy_air_quality(self):
        """Test AQI calculation for unhealthy air quality (PM2.5 > 150.4)."""
        pollutants = {"pm25": 200.0}
        aqi = self.service._get_aqi_from_pollutants(pollutants)
        assert 201 <= aqi <= 300

    def test_aqi_calculation_hazardous_air_quality(self):
        """Test AQI calculation for hazardous air quality (PM2.5 > 500.4)."""
        pollutants = {"pm25": 600.0}
        aqi = self.service._get_aqi_from_pollutants(pollutants)
        assert aqi == 500

    @patch('requests.get')
    def test_get_air_quality_data_success(self, mock_get):
        """Test successful air quality data retrieval."""
        # Mock the geocoding API response
        geocoding_response = Mock()
        geocoding_response.status_code = 200
        geocoding_response.json.return_value = [{
            "name": "London",
            "lat": 51.5085,
            "lon": -0.1257,
            "country": "GB"
        }]
        
        # Mock the air quality API response
        air_quality_response = Mock()
        air_quality_response.status_code = 200
        air_quality_response.json.return_value = {
            "coord": {"lon": -0.1257, "lat": 51.5085},
            "list": [{
                "main": {"aqi": 2},
                "components": {
                    "co": 200.0,
                    "no": 0.0,
                    "no2": 10.0,
                    "o3": 50.0,
                    "so2": 5.0,
                    "pm2_5": 15.0,
                    "pm10": 25.0,
                    "nh3": 0.0
                },
                "dt": 1640995200
            }]
        }
        
        # Configure mock to return different responses for different calls
        mock_get.side_effect = [geocoding_response, air_quality_response]

        # Test the method
        result = self.service.get_air_quality_data("London", "GB")

        # Assertions
        assert result is not None
        assert isinstance(result, AirQualityData)
        assert result.aqi == 57  # Calculated from PM2.5 = 15.0
        assert result.pm25 == 15.0
        assert result.pm10 == 25.0
        assert result.o3 == 50.0
        assert result.no2 == 10.0
        assert result.so2 == 5.0
        assert result.co == 200.0

    @patch('requests.get')
    def test_get_air_quality_data_api_error(self, mock_get):
        """Test air quality data retrieval with API error."""
        # Mock API error response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # Test the method
        result = self.service.get_air_quality_data("InvalidCity", "XX")

        # Should return None on error
        assert result is None

    @patch('requests.get')
    def test_get_air_quality_data_network_error(self, mock_get):
        """Test air quality data retrieval with network error."""
        # Mock network error
        mock_get.side_effect = Exception("Network error")

        # Test the method
        result = self.service.get_air_quality_data("London", "GB")

        # Should return None on error
        assert result is None

    def test_get_health_recommendations_good_air_quality(self):
        """Test health recommendations for good air quality."""
        aqi = 25
        recommendations = self.service._get_health_recommendations(aqi)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert any("good" in rec.lower() for rec in recommendations)

    def test_get_health_recommendations_unhealthy_air_quality(self):
        """Test health recommendations for unhealthy air quality."""
        aqi = 175
        recommendations = self.service._get_health_recommendations(aqi)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert any("sensitive" in rec.lower() or "avoid" in rec.lower() for rec in recommendations)

    def test_get_health_recommendations_hazardous_air_quality(self):
        """Test health recommendations for hazardous air quality."""
        aqi = 450
        recommendations = self.service._get_health_recommendations(aqi)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert any("everyone" in rec.lower() or "avoid" in rec.lower() for rec in recommendations)


class TestAirQualityData:
    """Test cases for the AirQualityData model."""

    def test_air_quality_data_creation(self):
        """Test creating an AirQualityData instance."""
        data = AirQualityData(
            aqi=50,
            pm25=12.5,
            pm10=20.0,
            location="London, GB",
            timestamp="2024-01-15T10:30:00Z"
        )
        
        assert data.aqi == 50
        assert data.pm25 == 12.5
        assert data.pm10 == 20.0
        assert data.location == "London, GB"
        assert data.timestamp == "2024-01-15T10:30:00Z"

    def test_air_quality_data_optional_fields(self):
        """Test creating AirQualityData with only required fields."""
        data = AirQualityData()
        
        assert data.aqi is None
        assert data.pm25 is None
        assert data.location is None

    def test_air_quality_data_with_recommendations(self):
        """Test creating AirQualityData with health recommendations."""
        recommendations = [
            "Air quality is good",
            "Enjoy outdoor activities"
        ]
        
        data = AirQualityData(
            aqi=25,
            health_recommendations=recommendations
        )
        
        assert data.health_recommendations == recommendations
        assert len(data.health_recommendations) == 2


# Basic smoke test for the main application
def test_basic_imports():
    """Test that all main modules can be imported without errors."""
    try:
        # Test importing the service directly instead of main app
        from services.air_quality_service import AirQualityService
        from models.air_quality import AirQualityData
        assert AirQualityService is not None
        assert AirQualityData is not None
    except ImportError as e:
        pytest.fail(f"Failed to import modules: {e}")


if __name__ == "__main__":
    # Run tests if this file is executed directly
    pytest.main([__file__, "-v"])
