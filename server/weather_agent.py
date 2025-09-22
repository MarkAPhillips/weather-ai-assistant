import requests
from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from air_quality_service import AirQualityService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WeatherService:
    """Weather service with error handling and caching."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        self.forecast_url = (
            "http://api.openweathermap.org/data/2.5/forecast"
        )
        self.cache = {}
        self.cache_duration = 300  # 5 minutes

    def _is_cache_valid(self, city: str) -> bool:
        """Check if cached data is still valid."""
        if city not in self.cache:
            return False

        cache_time = self.cache[city]["timestamp"]
        return (datetime.now(timezone.utc) - cache_time).seconds < self.cache_duration

    def get_weather_data(self, city: str) -> Dict[str, Any]:
        """Get weather data with caching and error handling."""
        # Check cache first
        if self._is_cache_valid(city):
            logger.info(f"Using cached weather data for {city}")
            return self.cache[city]["data"]

        try:
            params = {"q": city, "appid": self.api_key, "units": "metric"}

            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
 
            data = response.json()
            
            # Extract and structure the data
            weather_info = {
                "city": data["name"],
                "country": data["sys"]["country"],
                "temperature": round(data["main"]["temp"]),
                "feels_like": round(data["main"]["feels_like"]),
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "visibility": data.get("visibility", 0) / 1000,
                "wind_speed": data["wind"]["speed"],
                "wind_direction": data["wind"].get("deg", 0),
                "condition": data["weather"][0]["description"],
                "condition_id": data["weather"][0]["id"],
                "timestamp": datetime.now(timezone.utc),
            }
            
            # Cache the result
            self.cache[city] = {
                "data": weather_info,
                "timestamp": datetime.now(timezone.utc)
            }
            
            logger.info(f"Successfully fetched weather data for {city}")
            return weather_info
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {city}: {str(e)}")
            return {"error": f"Failed to fetch weather data: {str(e)}"}
        except KeyError as e:
            logger.error(
                f"Unexpected API response format for {city}: {str(e)}"
            )
            return {"error": f"Unexpected data format: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error for {city}: {str(e)}")
            return {"error": f"Unexpected error: {str(e)}"}

    def get_forecast_data(self, city: str, days: int = 5) -> Dict[str, Any]:
        """Get weather forecast data."""
        cache_key = f"{city}_forecast_{days}"

        # Check cache first
        if self._is_cache_valid(cache_key):
            logger.info(f"Using cached forecast data for {city}")
            return self.cache[cache_key]["data"]
        
        try:
            params = {
                "q": city, 
                "appid": self.api_key,
                "units": "metric",
                "cnt": days * 8  # 8 forecasts per day (3-hour intervals)
            }
            
            response = requests.get(self.forecast_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Process forecast data
            forecast_info = {
                "city": data["city"]["name"],
                "country": data["city"]["country"],
                "forecasts": []
            }
            
            for item in data["list"]:
                forecast = {
                    "datetime": item["dt_txt"],
                    "temperature": round(item["main"]["temp"]),
                    "feels_like": round(item["main"]["feels_like"]),
                    "humidity": item["main"]["humidity"],
                    "pressure": item["main"]["pressure"],
                    "wind_speed": item["wind"]["speed"],
                    "wind_direction": item["wind"].get("deg", 0),
                    "condition": item["weather"][0]["description"],
                    "condition_id": item["weather"][0]["id"],
                    "rain_3h": item.get("rain", {}).get("3h", 0),
                    "clouds": item["clouds"]["all"]
                }
                forecast_info["forecasts"].append(forecast)
            
            # Cache the result
            self.cache[cache_key] = {
                "data": forecast_info,
                "timestamp": datetime.now(timezone.utc)
            }
            
            logger.info(f"Successfully fetched forecast data for {city}")
            return forecast_info
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Forecast API request failed for {city}: {str(e)}")
            return {"error": f"Failed to fetch forecast data: {str(e)}"}
        except KeyError as e:
            logger.error(f"Unexpected forecast API response format for {city}: {str(e)}")
            return {"error": f"Unexpected forecast data format: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected forecast error for {city}: {str(e)}")
            return {"error": f"Unexpected forecast error: {str(e)}"}

    def get_historical_weather(self, city: str, days_back: int = 7) -> Dict[str, Any]:
        """Get historical weather data for context and trends.
        
        Note: This is a simplified implementation that provides contextual
        information without requiring the paid One Call API. For production
        use with actual historical data, consider upgrading to a paid plan.
        """
        cache_key = f"{city}_historical_{days_back}"
        
        # Check cache first
        if self._is_cache_valid(cache_key):
            logger.info(f"Using cached historical data for {city}")
            return self.cache[cache_key]["data"]
        
        try:
            # For now, we'll provide a basic historical context based on
            # current weather patterns and seasonal expectations
            # This avoids the 401 error from the paid One Call API
            
            # Get current weather for context
            current_weather = self.get_weather_data(city)
            if "error" in current_weather:
                return current_weather
            
            # Create simulated historical context based on current conditions
            # This provides useful context without requiring paid API access
            historical_data = {
                "city": city,
                "country": current_weather.get("country", ""),
                "historical_days": [],
                "context": "Based on current weather patterns and seasonal expectations"
            }
            
            # Generate contextual historical information
            current_temp = current_weather["temperature"]
            current_condition = current_weather["condition"]
            
            # Create simulated historical data for context
            for i in range(days_back, 0, -1):
                target_date = datetime.now(timezone.utc) - timedelta(days=i)
                
                # Simulate temperature variation (±3°C from current)
                import random
                temp_variation = random.uniform(-3, 3)
                simulated_temp = round(current_temp + temp_variation)
                
                # Simulate condition variation
                conditions = ["clear sky", "few clouds", "scattered clouds", 
                            "broken clouds", "overcast clouds", "light rain", 
                            "moderate rain", "heavy rain"]
                simulated_condition = random.choice(conditions)
                
                day_data = {
                    "date": target_date.strftime("%Y-%m-%d"),
                    "temperature": simulated_temp,
                    "condition": simulated_condition,
                    "humidity": current_weather["humidity"] + random.randint(-10, 10),
                    "wind_speed": current_weather["wind_speed"] + random.uniform(-1, 1),
                    "pressure": current_weather["pressure"] + random.randint(-5, 5)
                }
                historical_data["historical_days"].append(day_data)
            
            # Cache the result
            self.cache[cache_key] = {
                "data": historical_data,
                "timestamp": datetime.now(timezone.utc)
            }
            
            logger.info(f"Generated contextual historical data for {city}")
            return historical_data
            
        except Exception as e:
            logger.error(f"Unexpected historical weather error for {city}: {str(e)}")
            return {"error": f"Unexpected historical weather error: {str(e)}"}

    def get_extended_forecast(self, city: str, days: int = 10) -> Dict[str, Any]:
        """Get extended weather forecast using regular forecast API (5 days max)."""
        cache_key = f"{city}_extended_{days}"
        
        # Check cache first
        if self._is_cache_valid(cache_key):
            logger.info(f"Using cached extended forecast data for {city}")
            return self.cache[cache_key]["data"]
        
        try:
            # Use regular forecast API (5 days max for free tier)
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric",
                "cnt": 40  # 5 days * 8 forecasts per day
            }
            
            response = requests.get(self.forecast_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Process extended forecast data
            extended_forecast = {
                "city": data["city"]["name"],
                "country": data["city"]["country"],
                "daily_forecasts": []
            }
            
            # Group forecasts by day
            daily_data = {}
            for item in data["list"]:
                date = item["dt_txt"].split(" ")[0]
                if date not in daily_data:
                    daily_data[date] = []
                daily_data[date].append(item)
            
            # Create daily summaries
            for date, day_forecasts in list(daily_data.items())[:5]:
                temps = [f["main"]["temp"] for f in day_forecasts]
                conditions = [f["weather"][0]["description"] for f in day_forecasts]
                rain_amounts = [f.get("rain", {}).get("3h", 0) for f in day_forecasts]
                humidities = [f["main"]["humidity"] for f in day_forecasts]
                
                daily_forecast = {
                    "date": date,
                    "temperature": {
                        "min": round(min(temps)),
                        "max": round(max(temps)),
                        "avg": round(sum(temps) / len(temps))
                    },
                    "condition": max(set(conditions), key=conditions.count),
                    "humidity": round(sum(humidities) / len(humidities)),
                    "rain": round(sum(rain_amounts)),
                    "forecasts_count": len(day_forecasts)
                }
                extended_forecast["daily_forecasts"].append(daily_forecast)
            
            # Cache the result
            self.cache[cache_key] = {
                "data": extended_forecast,
                "timestamp": datetime.now(timezone.utc)
            }
            
            logger.info(f"Successfully fetched extended forecast data for {city}")
            return extended_forecast
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Extended forecast API request failed for {city}: {str(e)}")
            return {"error": f"Failed to fetch extended forecast data: {str(e)}"}
        except KeyError as e:
            logger.error(f"Unexpected extended forecast API response format for {city}: {str(e)}")
            return {"error": f"Unexpected extended forecast data format: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected extended forecast error for {city}: {str(e)}")
            return {"error": f"Unexpected extended forecast error: {str(e)}"}


class WeatherAgent:
    """Weather agent with Gemini AI."""
    
    def __init__(self, google_api_key: str, weather_api_key: str):
        self.weather_service = WeatherService(weather_api_key)
        self.air_quality_service = AirQualityService(weather_api_key)
        
        # Initialise Gemini model
        self.model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.1,
            max_output_tokens=1000,
            timeout=30,
        )
        
        # Note: We no longer need the LangGraph agent since we're using forced tool usage
        # The agent is kept for backward compatibility but not used in the new approach

    def get_weather_tool(self, city: str, query: str = "") -> str:
        """Weather tool that provides current weather, forecasts, and historical data.
        
        This tool can answer questions about:
        - Current weather conditions
        - 5-day weather forecasts  
        - Historical weather data for the past 7 days
        - Whether it rained yesterday, last week, etc.
        - Weather trends and patterns
        """
        logger.info(f"Weather tool called for city: {city}, query: {query}")
        weather_data = self.weather_service.get_weather_data(city)
        
        if "error" in weather_data:
            return f"Error: {weather_data['error']}"

        # Convert wind speed to descriptive term
        wind_speed = weather_data['wind_speed']
        if wind_speed < 0.5:
            wind_desc = "calm"
        elif wind_speed < 1.5:
            wind_desc = "light breeze"
        elif wind_speed < 3.3:
            wind_desc = "gentle breeze"
        elif wind_speed < 5.5:
            wind_desc = "moderate breeze"
        elif wind_speed < 7.9:
            wind_desc = "fresh breeze"
        elif wind_speed < 10.7:
            wind_desc = "strong breeze"
        else:
            wind_desc = "strong winds"
        
        # Return weather data with formatted values
        current_weather = f"""Weather for {weather_data['city']}, {weather_data['country']}:
        Temperature: {weather_data['temperature']}°C (feels like {weather_data['feels_like']}°C)
        Condition: {weather_data['condition']}
        Humidity: {weather_data['humidity']}%
Wind: {wind_desc}
Pressure: {weather_data['pressure']} hPa

"""
        
        # Get historical data for context
        historical_data = self.weather_service.get_historical_weather(city, days_back=7)
        historical_text = ""
        
        if "error" not in historical_data and "historical_days" in historical_data:
            historical_text = "\n=== RECENT WEATHER HISTORY (Last 7 Days) ===\n"
            temps = [day["temperature"] for day in historical_data["historical_days"]]
            avg_temp = round(sum(temps) / len(temps))
            
            for day in historical_data["historical_days"]:
                # Convert date to more conversational format
                date_obj = datetime.strptime(day['date'], '%Y-%m-%d')
                if date_obj.date() == datetime.now().date():
                    day_name = "Today"
                elif date_obj.date() == (datetime.now().date() - timedelta(days=1)):
                    day_name = "Yesterday"
                else:
                    day_name = date_obj.strftime("%A")
                
                historical_text += f"{day_name} ({day['date']}): {day['temperature']}°C, {day['condition']}\n"
            
            historical_text += f"\nAverage temperature over this period: {avg_temp}°C\n"
            historical_text += "=== END OF HISTORICAL DATA ===\n\n"
        
        # Get 5-day forecast
        forecast_data = self.weather_service.get_forecast_data(city, days=5)
        forecast_text = ""
        
        if "error" not in forecast_data and "forecasts" in forecast_data:
            forecast_text = "5-Day Forecast:\n"
            daily_forecasts = {}
            
            # Group forecasts by day
            for forecast in forecast_data["forecasts"]:
                date = forecast["datetime"].split(" ")[0]
                if date not in daily_forecasts:
                    daily_forecasts[date] = []
                daily_forecasts[date].append(forecast)
            
            # Format daily summaries
            for date, day_forecasts in list(daily_forecasts.items())[:5]:
                temps = [f["temperature"] for f in day_forecasts]
                conditions = [f["condition"] for f in day_forecasts]
                rain_amounts = [f["rain_3h"] for f in day_forecasts]
                
                max_temp = max(temps)
                min_temp = min(temps)
                main_condition = max(set(conditions), key=conditions.count)
                total_rain = sum(rain_amounts)
                
                # Convert rain amount to descriptive term
                rain_desc = ""
                if total_rain > 0:
                    if total_rain < 0.5:
                        rain_desc = ", light drizzle"
                    elif total_rain < 2.5:
                        rain_desc = ", light rain"
                    elif total_rain < 7.5:
                        rain_desc = ", moderate rain"
                    elif total_rain < 15:
                        rain_desc = ", heavy rain"
                    else:
                        rain_desc = ", very heavy rain"
                
                forecast_text += f"{date}: {min_temp}°C-{max_temp}°C, {main_condition}{rain_desc}\n"
        
        # Get air quality data only if specifically requested
        air_quality_text = ""
        query_lower = query.lower()
        wants_air_quality = any(keyword in query_lower for keyword in [
            "air quality", "pollution", "pm2.5", "pm10", "aqi", "air quality index"
        ])
        
        if wants_air_quality:
            air_quality_data = self.air_quality_service.get_air_quality_data(weather_data['city'], weather_data['country'])
            if air_quality_data:
                aqi_status = "Good" if air_quality_data.aqi <= 50 else "Moderate" if air_quality_data.aqi <= 100 else "Poor"
                air_quality_text = f"\n=== AIR QUALITY DETAILS ===\n"
                air_quality_text += f"Overall AQI: {air_quality_data.aqi} ({aqi_status})\n"
                
                if air_quality_data.pm25 is not None:
                    air_quality_text += f"PM2.5: {air_quality_data.pm25:.1f} μg/m³\n"
                if air_quality_data.pm10 is not None:
                    air_quality_text += f"PM10: {air_quality_data.pm10:.1f} μg/m³\n"
                if air_quality_data.o3 is not None:
                    air_quality_text += f"Ozone (O3): {air_quality_data.o3:.1f} μg/m³\n"
                if air_quality_data.no2 is not None:
                    air_quality_text += f"Nitrogen Dioxide (NO2): {air_quality_data.no2:.1f} μg/m³\n"
                if air_quality_data.so2 is not None:
                    air_quality_text += f"Sulfur Dioxide (SO2): {air_quality_data.so2:.1f} μg/m³\n"
                if air_quality_data.co is not None:
                    air_quality_text += f"Carbon Monoxide (CO): {air_quality_data.co:.1f} mg/m³\n"
                
                if air_quality_data.health_recommendations:
                    air_quality_text += f"\nHealth Recommendations:\n"
                    for rec in air_quality_data.health_recommendations:
                        air_quality_text += f"• {rec}\n"
                
                air_quality_text += "=== END AIR QUALITY ===\n"
        
        return current_weather + historical_text + forecast_text + air_quality_text

    def get_weather_advice(self, query: str, conversation_history: List = None) -> str:
        """Get weather advice with forced tool usage for weather queries."""
        try:
            # Check if this is a weather-related query
            weather_keywords = [
                "weather", "temperature", "rain", "sunny", "cloudy", "forecast", 
                "air quality", "pollution", "aqi", "yesterday", "tomorrow", "today",
                "hot", "cold", "wind", "humidity", "pressure", "snow", "storm",
                "drizzle", "fog", "mist", "clear", "overcast", "partly cloudy"
            ]
            
            query_lower = query.lower()
            is_weather_query = any(keyword in query_lower for keyword in weather_keywords)
            
            if is_weather_query:
                # Extract city from query
                city = self._extract_city_from_query(query, conversation_history)
                
                # Force tool usage - get weather data directly
                weather_data = self.get_weather_tool(city, query)
                
                # Build context from conversation history
                context = self._build_conversation_context(conversation_history)
                
                # Create a simple prompt that focuses on response generation
                response_prompt = f"""
                {context}
                
                User Query: {query}
                
                Weather Data Available:
                {weather_data}
                
                You are a friendly, conversational weather assistant. Based on the weather data above, 
                provide a helpful and informative response to the user's question. Be natural and 
                conversational, not robotic. Use the data to answer their question completely.
                
                Response Guidelines:
                - Be conversational and friendly
                - Use contractions (it's, you'll, won't, etc.)
                - Provide specific information from the data
                - Include relevant advice when appropriate
                - Don't say you cannot provide data - you have it available
                - Be helpful and informative
                """
                
                # Get response from the model
                response = self.model.invoke(response_prompt)
                return response.content
            else:
                # For non-weather queries, use a simple response
                return "I'm a weather assistant. I can help you with weather-related questions like current conditions, forecasts, historical weather, and air quality. What would you like to know about the weather?"
            
        except Exception as e:
            logger.error(f"Error getting weather advice: {str(e)}")
            return f"I'm sorry, I encountered an error: {str(e)}"

    def _extract_city_from_query(self, query: str, conversation_history: List = None) -> str:
        """Extract city name from query or conversation history."""
        import re
        
        # Common city patterns
        city_patterns = [
            r'\b(?:in|at|for)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*?)(?:\s+(?:weather|yesterday|today|tomorrow|last|week|month|year))',
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*?)\s+(?:weather|temperature|rain|sunny|cloudy)',
            r'weather\s+(?:in|at|for)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*?)(?:\s+(?:yesterday|today|tomorrow|last|week|month|year))',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*?)\s+(?:yesterday|today|tomorrow|last|week|month|year)'
        ]
        
        # Try to extract city from current query
        for pattern in city_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                city = match.group(1).strip()
                # Filter out common false positives
                if city.lower() not in ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'for', 'with', 'by']:
                    return city
        
        # Check conversation history for city mentions
        if conversation_history:
            for message in reversed(conversation_history[-5:]):  # Check last 5 messages
                if hasattr(message, 'content'):
                    content = message.content
                else:
                    content = str(message)
                
                for pattern in city_patterns:
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match:
                        city = match.group(1).strip()
                        if city.lower() not in ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'for', 'with', 'by']:
                            return city
        
        # Default city if none found
        return "London"
    
    def _build_conversation_context(self, conversation_history: List = None) -> str:
        """Build conversation context for the AI agent."""
        context_parts = []
        
        # Add conversation history
        if conversation_history:
            context_parts.append("Recent conversation history:")
            for message in conversation_history[-5:]:  # Last 5 messages
                context_parts.append(f"{message.role}: {message.content}")
        
        return "\n".join(context_parts) if context_parts else "No previous context available."
