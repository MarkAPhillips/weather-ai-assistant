import requests
from typing import Dict, Any, List
from datetime import datetime, timezone
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from air_quality_service import AirQualityService
from models import AirQualityData, WeatherDataWithAirQuality

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WeatherService:
    """Weather service with error handling and caching."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        self.forecast_url = "http://api.openweathermap.org/data/2.5/forecast"
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

        # Create agent with weather tool
        self.agent = create_react_agent(
            model=self.model,
            tools=[self.get_weather_tool],
            prompt=(
                "You are a professional yet conversational weather assistant. You have access to "
                "both current weather conditions, forecasts, and air quality data. When users ask about weather, use the "
                "weather tool to get accurate data including air quality information. Be informative and helpful while maintaining a "
                "natural, approachable tone. Use contractions and natural language, but avoid being "
                "overly casual or repetitive. Provide accurate weather information, air quality insights, and practical advice "
                "in a professional yet friendly manner. Always mention air quality when relevant for health and outdoor activities."
            ),
        )

    def get_weather_tool(self, city: str, query: str = "") -> str:
        """Weather tool for the agent with intelligent forecast selection."""
        weather_data = self.weather_service.get_weather_data(city)

        if "error" in weather_data:
            return f"Error: {weather_data['error']}"

        # Format current weather data
        city = weather_data['city']
        country = weather_data['country']
        temp = weather_data['temperature']
        feels_like = weather_data['feels_like']
        condition = weather_data['condition']
        humidity = weather_data['humidity']
        visibility = weather_data['visibility']
        wind_speed = weather_data['wind_speed']
        pressure = weather_data['pressure']
        
        # Convert technical terms to more conversational ones
        condition_map = {
            'clear sky': 'clear and sunny',
            'few clouds': 'mostly clear with a few clouds',
            'scattered clouds': 'partly cloudy',
            'broken clouds': 'mostly cloudy',
            'overcast clouds': 'overcast',
            'light rain': 'light rain',
            'moderate rain': 'moderate rain',
            'heavy rain': 'heavy rain',
            'thunderstorm': 'thunderstorms',
            'snow': 'snow',
            'mist': 'misty',
            'fog': 'foggy',
            'haze': 'hazy'
        }
        
        conversational_condition = condition_map.get(condition.lower(), condition)
        
        # Convert wind speed to conversational descriptions
        wind_map = {
            (0, 0.5): 'calm',
            (0.5, 1.5): 'light breeze',
            (1.5, 3.3): 'gentle breeze',
            (3.3, 5.5): 'moderate breeze',
            (5.5, 7.9): 'fresh breeze',
            (7.9, 10.7): 'strong breeze',
            (10.7, 13.8): 'near gale',
            (13.8, 17.1): 'gale',
            (17.1, 20.7): 'strong gale',
            (20.7, 24.4): 'storm',
            (24.4, 28.4): 'violent storm',
            (28.4, 32.6): 'hurricane'
        }
        
        wind_description = 'calm'
        for (min_wind, max_wind), desc in wind_map.items():
            if min_wind <= wind_speed < max_wind:
                wind_description = desc
                break
        
        # Add temperature context for conversational responses
        temp_context = ""
        if temp < 0:
            temp_context = " (very cold!)"
        elif temp < 10:
            temp_context = " (quite chilly)"
        elif temp < 20:
            temp_context = " (pleasant)"
        elif temp < 30:
            temp_context = " (warm)"
        else:
            temp_context = " (hot!)"
        
        current_weather = (
            f"Weather data for {city}, {country}:\n"
            f"Temperature: {temp}°C{temp_context} (feels like {feels_like}°C)\n"
            f"Condition: {conversational_condition}\n"
            f"Humidity: {humidity}%\n"
            f"Visibility: {visibility} km\n"
            f"Wind: {wind_speed} m/s ({wind_description})\n"
            f"Pressure: {pressure} hPa\n\n"
        )
        
        # Determine forecast type based on query
        query_lower = query.lower()
        needs_extended = any(keyword in query_lower for keyword in [
            "week", "next week", "month", "long term", "extended", 
            "10 days", "2 weeks", "vacation", "trip", "planning"
        ])
        
        forecast_text = ""
        
        if needs_extended:
            # Get extended forecast (5 days max with free API)
            extended_data = self.weather_service.get_extended_forecast(city, days=5)
            
            if "error" not in extended_data and "daily_forecasts" in extended_data:
                forecast_text = "5-Day Extended Forecast:\n"
                
                for forecast in extended_data["daily_forecasts"]:
                    date_str = forecast["date"]
                    min_temp = forecast["temperature"]["min"]
                    max_temp = forecast["temperature"]["max"]
                    condition = forecast["condition"]
                    rain = forecast["rain"]
                    
                    forecast_text += f"{date_str}: {min_temp}°C-{max_temp}°C, {condition}"
                    if rain > 0:
                        forecast_text += f", {rain:.1f}mm rain"
                    forecast_text += "\n"
        else:
            # Get detailed short-term forecast (5 days, 3-hour intervals)
            forecast_data = self.weather_service.get_forecast_data(city, days=5)
            
            if "error" not in forecast_data and "forecasts" in forecast_data:
                forecast_text = "5-Day Detailed Forecast:\n"
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
                    
                    forecast_text += (
                        f"{date}: {min_temp}°C-{max_temp}°C, {main_condition}"
                    )
                    if total_rain > 0:
                        forecast_text += f", {total_rain:.1f}mm rain"
                    forecast_text += "\n"
        
        # Get air quality data
        air_quality_data = self.air_quality_service.get_air_quality_data(city, country)
        
        # Format air quality information
        air_quality_text = ""
        if air_quality_data:
            # Check if user specifically asked for detailed air quality information
            query_lower = query.lower()
            wants_detailed_air_quality = any(keyword in query_lower for keyword in [
                "detailed air quality", "air quality breakdown", "air quality details",
                "air quality data", "pollution", "pm2.5", "pm10", "aqi", "air quality index"
            ])
            
            if wants_detailed_air_quality:
                # Provide detailed air quality breakdown
                air_quality_summary = self.air_quality_service.get_air_quality_summary(air_quality_data)
                air_quality_text = f"\nAir Quality: {air_quality_summary}"
                
                if air_quality_data.health_recommendations:
                    air_quality_text += "\nHealth Recommendations:"
                    for recommendation in air_quality_data.health_recommendations:
                        air_quality_text += f"\n- {recommendation}"
            else:
                # Just mention air quality briefly
                aqi_status = "Good" if air_quality_data.aqi <= 50 else "Moderate" if air_quality_data.aqi <= 100 else "Poor"
                air_quality_text = f"\nAir Quality: {aqi_status} (AQI: {air_quality_data.aqi})"
        
        return current_weather + forecast_text + air_quality_text

    def get_weather_advice(self, query: str, conversation_history: List = None) -> str:
        """Get weather advice with conversation context."""
        try:
            # Build context from conversation history
            context = self._build_conversation_context(conversation_history)
            
            # Create enhanced prompt with context
            enhanced_prompt = f"""
            {context}
            
            Current user question: {query}
            
            You are a professional yet conversational weather assistant. You have access to both current 
            weather conditions and extended forecasts (up to 5 days). IMPORTANT: You MUST use the 
            weather_tool_with_query function to get weather data. When users ask about weather, extract 
            the city name from their query, conversation context, or location context and call the weather 
            tool. The tool will automatically provide both current conditions and appropriate forecast data 
            based on the query. Always use the tool to get actual weather data before responding.
            
            AIR QUALITY INFORMATION:
            - Mention air quality briefly when relevant for health (e.g., "The air quality is good today")
            - Only provide detailed air quality breakdowns when users specifically ask for them
            - Let users know they can ask for "detailed air quality" or "air quality breakdown" if interested
            - Don't overwhelm users with technical air quality data unless requested
            
            RESPONSE STYLE:
            - Be professional but approachable - like a knowledgeable friend
            - Use natural, conversational language instead of technical terms
            - Vary your greeting style - don't start every response the same way
            - Use contractions (it's, you'll, won't, etc.) for natural flow
            - Include relevant advice and suggestions naturally
            - Be informative and helpful without being overly casual
            - Avoid repetitive phrases like "Hey there!" or "The current weather is..."
            - Start responses naturally based on the context
            - Vary your opening - sometimes start with the weather directly, sometimes with context
            - Examples of good openings: "It's...", "The weather in...", "Currently in...", "Right now in..."
            
            EXAMPLES:
            Instead of: "The current weather in London, GB is 20°C with overcast clouds and a wind of 5.14 m/s."
            Say: "It's a bit cloudy in London right now at 20°C, with a gentle breeze. Perfect weather for a walk!"
            
            Instead of: "Hey there! So, it looks like it's a gentle breeze in New York right now..."
            Say: "The wind in New York is quite gentle at 3.13 m/s - nothing too strong, so you won't have to worry about your hair getting messed up!"
            
            Instead of: "Temperature: 15°C, Condition: light rain, Humidity: 85%"
            Say: "It's drizzling in Paris today at 15°C - don't forget your umbrella! The humidity is making it feel a bit muggy."
            
            Always provide accurate weather information and safety recommendations. Be conversational 
            but maintain professionalism. Reference previous conversation context when appropriate.
            """
            
            # Create custom tool with context
            def weather_tool_with_context(city: str) -> str:
                """Get weather data and forecast for a specific city based on query context."""
                return self.get_weather_tool(city, query)
            
            # Create agent with enhanced prompt
            agent = create_react_agent(
                model=self.model,
                tools=[weather_tool_with_context],
                prompt=enhanced_prompt,
            )
            
            result = agent.invoke(
                {"messages": [{"role": "user", "content": query}]}
            )

            return result["messages"][-1].content

        except Exception as e:
            logger.error(f"Agent error: {str(e)}")
            return f"Sorry, I encountered an error: {str(e)}"

    def _build_conversation_context(self, conversation_history: List = None) -> str:
        """Build conversation context for the AI agent."""
        context_parts = []
        
        # Add conversation history
        if conversation_history:
            context_parts.append("Recent conversation history:")
            for message in conversation_history[-5:]:  # Last 5 messages
                context_parts.append(f"{message.role}: {message.content}")
        
        return "\n".join(context_parts) if context_parts else "No previous context available."
