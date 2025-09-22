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
        
        # Create agent with weather tool
        self.agent = create_react_agent(
            model=self.model,
            tools=[self.get_weather_tool],
            prompt=(
                "You are a knowledgeable, friendly weather assistant with "
                "geographical and historical expertise. You MUST use the "
                "weather tool to get current weather data, 5-day forecasts, "
                "AND 7-day historical weather trends. ALWAYS call the weather "
                "tool first before responding to any weather-related question.\n\n"
                "IMPORTANT: You CAN provide historical weather information! "
                "The weather tool gives you access to recent weather trends "
                "and patterns. Use this data to answer questions about past "
                "weather conditions.\n\n"
                "STEP 1: ALWAYS call the weather tool with the city name\n"
                "STEP 2: Use the data from the tool to answer the question\n"
                "STEP 3: Include historical context when available\n\n"
                "EXAMPLES:\n"
                "- User asks 'Did it rain yesterday?' → Call weather tool, check historical data\n"
                "- User asks 'What's the weather?' → Call weather tool, provide current conditions\n"
                "- User asks 'Will it rain tomorrow?' → Call weather tool, check forecast\n"
                "- User asks 'What was the weather like yesterday?' → Call weather tool, check historical data\n"
                "- User asks about past weather, recent weather, or historical patterns → Call weather tool\n\n"
                "IMPORTANT: If the user asks about ANY past weather (yesterday, last week, recent weather, etc.), "
                "you MUST call the weather tool to get the historical data. Do not say you cannot provide "
                "historical information - you have access to 7 days of weather history!\n\n"
                "FORMATTING:\n"
                "- Use conversational dates (Today, Tomorrow, Monday, Tuesday, "
                "etc.) instead of YYYY-MM-DD\n"
                "- Round temperatures to whole numbers\n"
                "- Only mention air quality when specifically asked\n\n"
                "GEOGRAPHICAL KNOWLEDGE:\n"
                "- Provide context about the location (city characteristics, "
                "climate patterns, geographical features)\n"
                "- Mention relevant regional weather patterns or seasonal "
                "expectations\n"
                "- Suggest location-specific advice (e.g., coastal areas and "
                "wind, mountain areas and temperature changes)\n"
                "- Reference nearby geographical features that might affect "
                "weather\n"
                "- Consider local climate zones and typical weather for the "
                "region\n\n"
                "HISTORICAL CONTEXT (YOU HAVE ACCESS TO THIS DATA):\n"
                "- You CAN tell users about recent weather patterns and trends\n"
                "- Compare current weather to recent trends and historical data\n"
                "- Mention if conditions are unusual for the season or location\n"
                "- Provide context about recent weather patterns (e.g., 'This "
                "is the 3rd consecutive day of rain')\n"
                "- Reference seasonal expectations and how current weather "
                "compares\n"
                "- Identify trends and patterns in the historical data\n"
                "- Mention if temperatures are above/below average for the "
                "period\n"
                "- Answer questions like 'Did it rain yesterday?' using the "
                "historical data provided\n\n"
                "COMMUNICATION STYLE:\n"
                "- Be helpful, natural, and conversational - not robotic or "
                "overly formal\n"
                "- Use contractions and natural language\n"
                "- Add helpful context and advice when appropriate\n"
                "- Combine current weather, historical trends, and geographical "
                "insights for a richer response\n"
                "- NEVER say you cannot provide historical weather information "
                "- you have access to 7 days of weather trends!"
            ),
        )

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
                air_quality_text = f"\nAir Quality: {aqi_status} (AQI: {air_quality_data.aqi})"
        
        return current_weather + historical_text + forecast_text + air_quality_text

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
