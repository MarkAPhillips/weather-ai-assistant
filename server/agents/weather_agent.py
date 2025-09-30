from typing import List
from datetime import datetime, timedelta
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from services.weather_service import WeatherService
from services.air_quality_service import AirQualityService
from services.weaviate_service import WeaviateService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WeatherAgent:
    """Weather agent with Gemini AI."""

    def __init__(self, google_api_key: str, weather_api_key: str):
        self.weather_service = WeatherService(weather_api_key)
        self.air_quality_service = AirQualityService(weather_api_key)
        self.weaviate_service = WeaviateService()

        # Initialise Gemini model
        self.model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.1,
            max_output_tokens=1000,
            timeout=30,
        )

        # Initialize LangGraph memory
        self.memory = MemorySaver()

        # Store current conversation history for context
        self._current_conversation_history = []

        # Initialize agent (will be created lazily when first used)
        self.agent = None

    def __del__(self):
        """Cleanup method to close Weaviate connection."""
        if hasattr(self, 'weaviate_service'):
            self.weaviate_service.close()

    def close(self):
        """Close all service connections."""
        if hasattr(self, 'weaviate_service'):
            self.weaviate_service.close()

    def get_weather_tool(self, city: str, query: str = "") -> str:
        """Weather tool for current weather, forecasts, and historical data.

        This tool can answer questions about:
        - Current weather conditions
        - 5-day weather forecasts
        - Historical weather data for the past 7 days
        - Whether it rained yesterday, last week, etc.
        - Weather trends and patterns
        - Air quality information
        """
        logger.info(f"Weather tool called for city: {city}, query: {query}")

        if not city:
            return ("I need to know which city you're asking about. "
                    "Please specify a city name.")
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
        Temperature: {weather_data['temperature']}°C
        (feels like {weather_data['feels_like']}°C)
        Condition: {weather_data['condition']}
        Humidity: {weather_data['humidity']}%
        Wind: {wind_desc}
        Pressure: {weather_data['pressure']} hPa

"""

        # Get historical data for context
        historical_data = self.weather_service.get_historical_weather(
            city, days_back=7)
        historical_text = ""

        if ("error" not in historical_data and
                "historical_days" in historical_data):
            historical_text = "\n=== RECENT WEATHER HISTORY (Last 7 Days) ===\n"
            temps = [day["temperature"] for day in
                     historical_data["historical_days"]]
            avg_temp = round(sum(temps) / len(temps))

            for day in historical_data["historical_days"]:
                # Convert date to more conversational format
                date_obj = datetime.strptime(day['date'], '%Y-%m-%d')
                if date_obj.date() == datetime.now().date():
                    day_name = "Today"
                elif date_obj.date() == (datetime.now().date() -
                                         timedelta(days=1)):
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

        # Get air quality data - check both current query
        # and conversation context
        air_quality_text = ""
        query_lower = query.lower()

        # Check if air quality is requested in current query
        wants_air_quality = any(keyword in query_lower for keyword in [
            "air quality", "pollution", "pm2.5", "pm10",
            "aqi", "air quality index"
        ])

        # Also check conversation context for air quality requests
        if (not wants_air_quality and
                hasattr(self, '_current_conversation_history')):
            for message in self._current_conversation_history[-5:]:  # Last 5
                if message.role == "user":
                    msg_lower = message.content.lower()
                    if any(keyword in msg_lower for keyword in [
                        "air quality", "pollution", "pm2.5", "pm10",
                        "aqi", "air quality index"
                    ]):
                        wants_air_quality = True
                        break

        if wants_air_quality:
            air_quality_data = self.air_quality_service.get_air_quality_data(
                weather_data['city'], weather_data['country'])
            if air_quality_data:
                aqi_status = ("Good" if air_quality_data.aqi <= 50
                              else "Moderate" if air_quality_data.aqi <= 100
                              else "Poor")
                air_quality_text = "\n=== AIR QUALITY DETAILS ===\n"
                air_quality_text += f"Air Quality Index: {air_quality_data.aqi} ({aqi_status})\n"

                if air_quality_data.pm25 is not None:
                    air_quality_text += f"PM2.5: {air_quality_data.pm25:.1f} μg/m³\n"
                if air_quality_data.pm10 is not None:
                    air_quality_text += f"PM10: {air_quality_data.pm10:.1f} μg/m³\n"
                if air_quality_data.o3 is not None:
                    air_quality_text += f"Ozone (O3): {air_quality_data.o3:.1f} μg/m³\n"
                if air_quality_data.no2 is not None:
                    air_quality_text += f"NO2: {air_quality_data.no2:.1f} μg/m³\n"
                if air_quality_data.so2 is not None:
                    air_quality_text += f"SO2: {air_quality_data.so2:.1f} μg/m³\n"
                if air_quality_data.co is not None:
                    air_quality_text += f"CO: {air_quality_data.co:.1f} mg/m³\n"

                if air_quality_data.health_recommendations:
                    air_quality_text += "\nHealth Recommendations:\n"
                    for rec in air_quality_data.health_recommendations:
                        air_quality_text += f"- {rec}\n"

                air_quality_text += "=== END AIR QUALITY ===\n"

        return (current_weather + historical_text +
                forecast_text + air_quality_text)

    def search_weather_knowledge_tool(self, query: str) -> str:
        """Search weather knowledge base for explanations, phenomena, and educational content.

        This tool can answer questions about:
        - Weather phenomena explanations (how rain forms, why storms occur)
        - Weather safety advice and tips
        - Seasonal patterns and climate information
        - Weather forecasting concepts
        - Geographic weather patterns
        """
        logger.info(f"Weather knowledge tool called for query: {query}")

        if not self.weaviate_service.client:
            logger.info("Weaviate not available, skipping knowledge search")
            return ""

        try:
            # Search weather knowledge base
            knowledge_results = self.weaviate_service.search_weather_knowledge(
                query, limit=3)

            if not knowledge_results:
                logger.info("No weather knowledge found for query")
                return ""

            # Format the knowledge results
            knowledge_text = "\n=== WEATHER KNOWLEDGE ===\n"
            for i, result in enumerate(knowledge_results, 1):
                knowledge_text += f"{i}. {result.get('title', 'Weather Information')}\n"
                knowledge_text += f"   {result.get('content', '')}\n"
                if result.get('category'):
                    knowledge_text += f"   Category: {result['category']}\n"
                knowledge_text += "\n"

            knowledge_text += "=== END WEATHER KNOWLEDGE ===\n"
            logger.info(f"Retrieved {len(knowledge_results)} knowledge items")
            return knowledge_text

        except Exception as e:
            logger.error(f"Error searching weather knowledge: {e}")
            return ""

    def _create_agent(self):
        """Create the LangGraph agent with tools and memory."""
        self.agent = create_react_agent(
            model=self.model,
            tools=[self.get_weather_tool, self.search_weather_knowledge_tool],
            checkpointer=self.memory,
            prompt=(
                "You are a knowledgeable, friendly weather assistant. You have access to "
                "weather tools for current conditions and a knowledge base for explanations.\n\n"
                "Instructions:\n"
                "1. For current weather/forecasts: ALWAYS call the weather tool with the city name\n"
                "2. For weather explanations/phenomena: USE the knowledge search tool\n"
                "3. Use conversational dates (Today, Tomorrow, Monday) not YYYY-MM-DD\n"
                "4. Round temperatures to whole numbers\n"
                "5. Reference previous conversation when relevant\n"
                "6. If the user asks about air quality, pollution, or AQI, include air quality data\n"
                "7. Use conversation context to understand what city the user is referring to\n"
                "8. Combine factual data with educational knowledge when appropriate\n\n"
                "Be conversational, helpful, and provide both current information and "
                "educational context about weather phenomena and patterns."
            ),
        )

    def get_weather_advice(self, query: str, conversation_history: List = None,
                           user_locale: str = None,
                           session_id: str = None) -> str:
        """Get weather advice with LangGraph memory context."""
        try:
            # Create agent if it doesn't exist yet
            if self.agent is None:
                self._create_agent()

            # Use session_id for memory persistence,
            # generate one if not provided
            if not session_id:
                import uuid
                session_id = str(uuid.uuid4())

            # Configuration for LangGraph memory
            config = {"configurable": {"thread_id": session_id}}

            # Build messages for the agent
            from langchain_core.messages import HumanMessage
            messages = [HumanMessage(content=query)]

            # Invoke agent with memory configuration
            response = self.agent.invoke({"messages": messages}, config)

            # Extract the AI response from the agent output
            if isinstance(response, dict) and 'messages' in response:
                # Get the last AI message
                ai_messages = [msg for msg in response['messages']
                               if hasattr(msg, 'content') and msg.content and
                               hasattr(msg, 'type') and msg.type == 'ai']
                if ai_messages:
                    ai_response = ai_messages[-1].content
                    return ai_response

            # Fallback
            response_str = str(response)
            return response_str

        except Exception as e:
            logger.error(f"Agent error: {str(e)}")
            return ("I'm sorry, I'm having some technical difficulties right now. "
                    "Please try asking your question again in a moment.")
