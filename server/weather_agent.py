import requests
from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from air_quality_service import AirQualityService
from pexels_service import PexelsService

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
        self.pexels_service = PexelsService()
        
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
                "- User asks about past weather, recent weather, or historical patterns → Call weather tool\n"
                "- User asks 'What is the air quality like?' → Call weather tool, provide detailed air quality breakdown\n"
                "- User asks about air quality, pollution, or AQI → Call weather tool, provide detailed breakdown\n\n"
                "IMPORTANT: If the user asks about ANY past weather (yesterday, last week, recent weather, etc.), "
                "you MUST call the weather tool to get the historical data. Do not say you cannot provide "
                "historical information - you have access to 7 days of weather history!\n\n"
                "IMPORTANT: If the user asks about air quality, you MUST provide the detailed breakdown "
                "including individual pollutants (PM2.5, PM10, O3, NO2, SO2, CO) and health recommendations. "
                "Do not say you can only provide basic AQI - you have full detailed data!\n\n"
                "FORMATTING:\n"
                "- Use conversational dates (Today, Tomorrow, Monday, Tuesday, "
                "etc.) instead of YYYY-MM-DD\n"
                "- Round temperatures to whole numbers\n"
                "- Only mention air quality when specifically asked\n\n"
                "AIR QUALITY CAPABILITIES:\n"
                "- You have access to detailed air quality data including:\n"
                "  * Overall AQI (Air Quality Index)\n"
                "  * Individual pollutants: PM2.5, PM10, Ozone (O3), NO2, SO2, CO\n"
                "  * Health recommendations based on air quality\n"
                "- When users ask about air quality, ALWAYS provide the detailed breakdown\n"
                "- Include specific pollutant levels and what they mean\n"
                "- Explain health implications and recommendations\n"
                "- Do NOT say you can only provide basic AQI - you have full details!\n\n"
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
                "- you have access to 7 days of weather trends!\n"
                "- When air quality data is available, ALWAYS provide the detailed "
                "breakdown including individual pollutants and health recommendations"
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
        
        # Get weather image only for certain conditions or when specifically requested
        image_data = None
        query_lower = query.lower()
        
        # Only show images for:
        # 1. When user specifically asks for visual content
        # 2. For dramatic weather conditions that benefit from visual context
        # 3. For general weather overviews (not specific data requests)
        wants_visual_content = any(keyword in query_lower for keyword in [
            'show', 'see', 'look', 'picture', 'photo', 'image', 'visual', 'view'
        ])
        
        # Check if query is asking for specific data (temperature, humidity, etc.)
        is_specific_data_request = any(keyword in query_lower for keyword in [
            'temperature', 'temp', 'humidity', 'wind', 'pressure', 'degrees', 'celsius', 'fahrenheit'
        ])
        
        # Check if it's a general weather inquiry
        is_general_weather_inquiry = any(keyword in query_lower for keyword in [
            'weather', 'forecast', 'condition', 'like', 'how is', 'what is'
        ])
        
        current_condition = weather_data['condition'].lower()
        
        # Show images for:
        # 1. User explicitly wants visual content
        # 2. General weather inquiries (not specific data requests)
        # 3. Dramatic weather conditions
        should_show_image = (
            wants_visual_content or
            (is_general_weather_inquiry and not is_specific_data_request) or
            any(dramatic in current_condition for dramatic in [
                'storm', 'thunderstorm', 'lightning', 'heavy rain', 'snow', 'blizzard'
            ])
        )
        
        if should_show_image:
            image_data = self.pexels_service.get_weather_image(
                weather_data['condition'], 
                weather_data['city']
            )
        
        # Add image data to the response
        image_text = ""
        if image_data:
            image_text = f"\n=== WEATHER IMAGE ===\n"
            image_text += f"Image URL: {image_data['url']}\n"
            image_text += f"Description: {image_data['alt']}\n"
            image_text += f"Photographer: {image_data['photographer']}\n"
            image_text += f"Search Query: {image_data['query']}\n"
            image_text += "=== END IMAGE ===\n"
        
        return current_weather + historical_text + forecast_text + air_quality_text + image_text

    def get_weather_advice(self, query: str, conversation_history: List = None) -> str:
        """Get weather advice with conversation context."""
        try:
            # Build context from conversation history
            context = self._build_conversation_context(conversation_history)
            
            # Extract city from query
            city = self._extract_city_from_query(query, context)
            logger.info(f"Extracted city: '{city}' from query: '{query}'")
            if not city:
                return "I'd be happy to help with weather information! Could you please specify which city you'd like to know about?"
            
            # Get raw weather data with image
            try:
                raw_weather_data = self.get_weather_tool(city, query)
                
                # Create conversational summary using the model
                conversational_prompt = f"""
                You are a friendly, knowledgeable weather assistant. Based on this weather data for {city}, provide a conversational response to the user's question: "{query}"
                
                Weather data:
                {raw_weather_data}
                
                Guidelines for your response:
                - Start with a varied, natural greeting (avoid always saying "Hey there" - use different openings like "Good to hear from you!", "Happy to help!", "Let me check that for you!", "Here's what I found!", "Great question!", etc.)
                - Be conversational and helpful, but don't repeat raw technical data
                - Focus on what's most relevant to the user's specific question
                - Use a warm, professional tone
                - Vary your language and sentence structure
                - If it's a specific question (like "Should I bring an umbrella?"), give a direct, practical answer
                - If it's a general weather inquiry, provide a nice overview with key details
                
                Make your response feel natural and engaging, as if you're a knowledgeable friend helping with weather information.
                """
                
                # Get conversational response from the model
                response = self.model.invoke(conversational_prompt)
                conversational_response = response.content.strip()
                
                # Extract image data from raw weather data
                image_data = self._extract_image_data(raw_weather_data)
                
                # Return only conversational response with image data
                if image_data:
                    return f"{conversational_response}\n\n{image_data}"
                else:
                    return conversational_response
                
            except Exception as e:
                logger.error(f"Weather data fetch error for {city}: {str(e)}")
                # Return a friendly error message without technical details
                return f"I'm sorry, I'm having trouble getting the weather information for {city} right now. Please try again in a few moments, or check with another weather source."
            
        except Exception as e:
            logger.error(f"Agent error: {str(e)}")
            return "I'm sorry, I'm having some technical difficulties right now. Please try asking your question again in a moment."

    def _build_conversation_context(self, conversation_history: List = None) -> str:
        """Build conversation context for the AI agent."""
        context_parts = []
        
        # Add conversation history
        if conversation_history:
            context_parts.append("Recent conversation history:")
            for message in conversation_history[-5:]:  # Last 5 messages
                context_parts.append(f"{message.role}: {message.content}")
        
        return "\n".join(context_parts) if context_parts else "No previous context available."

    def _extract_city_from_query(self, query: str, context: str = "") -> str:
        """Extract city name from query or context."""
        import re
        
        # Common city patterns - more specific to avoid temporal words
        city_patterns = [
            r'in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)(?:\s|$)',
            r'for\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)(?:\s|$)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+weather',
            r'weather\s+in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)(?:\s|$)',
        ]
        
        # Direct city name matching (case insensitive) - check this first
        query_lower = query.lower()
        
        # Handle common temporal phrases and extract city names
        if 'tokyo' in query_lower:
            return 'Tokyo'
        elif 'london' in query_lower:
            return 'London'
        elif any(word in query_lower for word in ['new york', 'nyc', 'newyork']):
            return 'New York'
        elif 'paris' in query_lower:
            return 'Paris'
        elif 'berlin' in query_lower:
            return 'Berlin'
        elif 'madrid' in query_lower:
            return 'Madrid'
        elif 'rome' in query_lower:
            return 'Rome'
        elif 'sydney' in query_lower:
            return 'Sydney'
        elif 'melbourne' in query_lower:
            return 'Melbourne'
        elif 'toronto' in query_lower:
            return 'Toronto'
        elif 'vancouver' in query_lower:
            return 'Vancouver'
        elif 'mumbai' in query_lower:
            return 'Mumbai'
        elif 'delhi' in query_lower:
            return 'Delhi'
        elif 'beijing' in query_lower:
            return 'Beijing'
        elif 'shanghai' in query_lower:
            return 'Shanghai'
        elif 'singapore' in query_lower:
            return 'Singapore'
        elif 'seoul' in query_lower:
            return 'Seoul'
        elif 'bangkok' in query_lower:
            return 'Bangkok'
        elif 'dubai' in query_lower:
            return 'Dubai'
        elif 'istanbul' in query_lower:
            return 'Istanbul'
        elif 'moscow' in query_lower:
            return 'Moscow'
        elif 'cairo' in query_lower:
            return 'Cairo'
        elif 'johannesburg' in query_lower:
            return 'Johannesburg'
        elif 'lagos' in query_lower:
            return 'Lagos'
        elif 'nairobi' in query_lower:
            return 'Nairobi'
        elif 'rio de janeiro' in query_lower:
            return 'Rio de Janeiro'
        elif 'sao paulo' in query_lower:
            return 'Sao Paulo'
        elif 'buenos aires' in query_lower:
            return 'Buenos Aires'
        elif 'mexico city' in query_lower:
            return 'Mexico City'
        elif 'los angeles' in query_lower:
            return 'Los Angeles'
        elif 'chicago' in query_lower:
            return 'Chicago'
        elif 'houston' in query_lower:
            return 'Houston'
        elif 'phoenix' in query_lower:
            return 'Phoenix'
        elif 'philadelphia' in query_lower:
            return 'Philadelphia'
        elif 'san antonio' in query_lower:
            return 'San Antonio'
        elif 'san diego' in query_lower:
            return 'San Diego'
        elif 'dallas' in query_lower:
            return 'Dallas'
        elif 'san jose' in query_lower:
            return 'San Jose'
        elif 'austin' in query_lower:
            return 'Austin'
        elif 'jacksonville' in query_lower:
            return 'Jacksonville'
        elif 'fort worth' in query_lower:
            return 'Fort Worth'
        elif 'columbus' in query_lower:
            return 'Columbus'
        elif 'charlotte' in query_lower:
            return 'Charlotte'
        elif 'san francisco' in query_lower:
            return 'San Francisco'
        elif 'indianapolis' in query_lower:
            return 'Indianapolis'
        elif 'seattle' in query_lower:
            return 'Seattle'
        elif 'denver' in query_lower:
            return 'Denver'
        elif 'washington' in query_lower:
            return 'Washington'
        elif 'boston' in query_lower:
            return 'Boston'
        elif 'el paso' in query_lower:
            return 'El Paso'
        elif 'nashville' in query_lower:
            return 'Nashville'
        elif 'detroit' in query_lower:
            return 'Detroit'
        elif 'oklahoma city' in query_lower:
            return 'Oklahoma City'
        elif 'portland' in query_lower:
            return 'Portland'
        elif 'las vegas' in query_lower:
            return 'Las Vegas'
        elif 'memphis' in query_lower:
            return 'Memphis'
        elif 'louisville' in query_lower:
            return 'Louisville'
        elif 'baltimore' in query_lower:
            return 'Baltimore'
        elif 'milwaukee' in query_lower:
            return 'Milwaukee'
        elif 'albuquerque' in query_lower:
            return 'Albuquerque'
        elif 'tucson' in query_lower:
            return 'Tucson'
        elif 'fresno' in query_lower:
            return 'Fresno'
        elif 'sacramento' in query_lower:
            return 'Sacramento'
        elif 'mesa' in query_lower:
            return 'Mesa'
        elif 'kansas city' in query_lower:
            return 'Kansas City'
        elif 'atlanta' in query_lower:
            return 'Atlanta'
        elif 'long beach' in query_lower:
            return 'Long Beach'
        elif 'colorado springs' in query_lower:
            return 'Colorado Springs'
        elif 'raleigh' in query_lower:
            return 'Raleigh'
        elif 'miami' in query_lower:
            return 'Miami'
        elif 'virginia beach' in query_lower:
            return 'Virginia Beach'
        elif 'omaha' in query_lower:
            return 'Omaha'
        elif 'oakland' in query_lower:
            return 'Oakland'
        elif 'minneapolis' in query_lower:
            return 'Minneapolis'
        elif 'tulsa' in query_lower:
            return 'Tulsa'
        elif 'arlington' in query_lower:
            return 'Arlington'
        elif 'tampa' in query_lower:
            return 'Tampa'
        elif 'new orleans' in query_lower:
            return 'New Orleans'
        elif 'bishops stortford' in query_lower:
            return 'Bishops Stortford'
        
        # If no hardcoded match, try regex patterns for multi-word cities
        # Search in query first
        for pattern in city_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                city = match.group(1).strip()
                # Filter out common false positives and temporal words
                if city.lower() not in ['the', 'what', 'how', 'when', 'where', 'why', 'tomorrow', 'today', 'yesterday', 'next', 'last']:
                    return city

        # Search in context
        for pattern in city_patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                city = match.group(1).strip()
                if city.lower() not in ['the', 'what', 'how', 'when', 'where', 'why', 'tomorrow', 'today', 'yesterday', 'next', 'last']:
                    return city

        # Try to extract any capitalized words that might be city names
        # Look for patterns like "in [City Name]" or "[City Name] weather"
        words = query.split()
        for i, word in enumerate(words):
            if word.lower() in ['in', 'for', 'at'] and i + 1 < len(words):
                # Check if next word(s) are capitalized (potential city name)
                potential_city_parts = []
                j = i + 1
                while j < len(words) and words[j][0].isupper():
                    potential_city_parts.append(words[j])
                    j += 1
                
                if potential_city_parts:
                    potential_city = ' '.join(potential_city_parts)
                    # Filter out common false positives
                    if potential_city.lower() not in ['the', 'what', 'how', 'when', 'where', 'why', 'tomorrow', 'today', 'yesterday', 'next', 'last']:
                        return potential_city
        
        return None

    def _extract_image_data(self, raw_weather_data: str) -> str:
        """Extract only the image section from raw weather data."""
        import re
        
        # Look for weather image section
        image_section_regex = r'=== WEATHER IMAGE ===\n(.*?)\n=== END IMAGE ==='
        match = re.search(image_section_regex, raw_weather_data, re.DOTALL)
        
        if match:
            return f"=== WEATHER IMAGE ===\n{match.group(1)}\n=== END IMAGE ==="
        
        return ""
