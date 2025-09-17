import requests
from typing import Dict, Any
from datetime import datetime
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WeatherService:
    """Weather service with error handling and caching."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        self.cache = {}
        self.cache_duration = 300  # 5 minutes

    def _is_cache_valid(self, city: str) -> bool:
        """Check if cached data is still valid."""
        if city not in self.cache:
            return False

        cache_time = self.cache[city]["timestamp"]
        return (datetime.now() - cache_time).seconds < self.cache_duration

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
                "temperature": round(data["main"]["temp"], 1),
                "feels_like": round(data["main"]["feels_like"], 1),
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "visibility": data.get("visibility", 0) / 1000,
                "wind_speed": data["wind"]["speed"],
                "wind_direction": data["wind"].get("deg", 0),
                "condition": data["weather"][0]["description"],
                "condition_id": data["weather"][0]["id"],
                "timestamp": datetime.now(),
            }

            # Cache the result
            self.cache[city] = {
                "data": weather_info,
                "timestamp": datetime.now()
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


class WeatherAgent:
    """Weather agent with Gemini AI."""

    def __init__(self, google_api_key: str, weather_api_key: str):
        self.weather_service = WeatherService(weather_api_key)

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
                "You are a professional weather assistant with location "
                "awareness. When users ask about 'today', 'here', or 'my "
                "location', use the provided location context. Provide "
                "accurate, helpful weather information and safety "
                "recommendations. Always consider driving safety, outdoor "
                "activities, and health implications. Be concise but "
                "informative in your responses."
            ),
        )

    def get_weather_tool(self, city: str) -> str:
        """Weather tool for the agent."""
        weather_data = self.weather_service.get_weather_data(city)

        if "error" in weather_data:
            return f"Error: {weather_data['error']}"

        # Format data for the AI agent
        city = weather_data['city']
        country = weather_data['country']
        temp = weather_data['temperature']
        feels_like = weather_data['feels_like']
        condition = weather_data['condition']
        humidity = weather_data['humidity']
        visibility = weather_data['visibility']
        wind_speed = weather_data['wind_speed']
        pressure = weather_data['pressure']
        
        return (
            f"Current weather in {city}, {country}:\n"
            f"Temperature: {temp}°C (feels like {feels_like}°C)\n"
            f"Condition: {condition}\n"
            f"Humidity: {humidity}%\n"
            f"Visibility: {visibility} km\n"
            f"Wind: {wind_speed} m/s\n"
            f"Pressure: {pressure} hPa"
        )

    def get_weather_advice(self, query: str) -> str:
        """Get weather advice using the AI agent."""
        try:
            result = self.agent.invoke(
                {"messages": [{"role": "user", "content": query}]}
            )

            return result["messages"][-1].content

        except Exception as e:
            logger.error(f"Agent error: {str(e)}")
            return f"Sorry, I encountered an error: {str(e)}"
