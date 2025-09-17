from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import requests
from datetime import datetime
from weather_agent import WeatherAgent
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

weather_agent = WeatherAgent(
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    weather_api_key=os.getenv("OPENWEATHER_API_KEY"),
)


class Location(BaseModel):
    latitude: float
    longitude: float


class WeatherQuery(BaseModel):
    query: str
    city: Optional[str] = None
    userLocation: Optional[Location] = None


class WeatherResponse(BaseModel):
    response: str
    city: Optional[str] = None
    usedLocation: bool = False
    timestamp: str


def get_city_from_coordinates(lat: float, lon: float) -> str:
    """Get city name from coordinates using OpenWeatherMap Geocoding API."""
    try:
        response = requests.get(
            "http://api.openweathermap.org/geo/1.0/reverse",
            params={
                'lat': lat,
                'lon': lon,
                'limit': 1,
                'appid': os.getenv("OPENWEATHER_API_KEY")
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        if data and len(data) > 0:
            return data[0]['name']
        return "Unknown Location"

    except Exception as e:
        print(f"Error getting city from coordinates: {e}")
        return "Unknown Location"


@app.post("/api/weather", response_model=WeatherResponse)
async def get_weather_advice(request: WeatherQuery):
    """Get weather advice from AI agent with optional geolocation."""
    try:
        used_location = False
        target_city = request.city

        # Use geolocation if provided and no specific city requested
        if request.userLocation and not request.city:
            target_city = get_city_from_coordinates(
                request.userLocation.latitude,
                request.userLocation.longitude
            )
            used_location = True

        # Add city context to query
        if target_city:
            full_query = f"{request.query} (Location: {target_city})"
        else:
            full_query = request.query

        response = weather_agent.get_weather_advice(full_query)

        return WeatherResponse(
            response=response,
            city=target_city,
            usedLocation=used_location,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Health check endpoint with service status."""
    try:
        # Check if weather agent is properly initialized
        agent_status = "healthy" if weather_agent else "unhealthy"

        # Check environment variables
        google_key = os.getenv("GOOGLE_API_KEY")
        weather_key = os.getenv("OPENWEATHER_API_KEY")
        env_status = "healthy" if google_key and weather_key else "unhealthy"

        overall_status = (
            "healthy" if agent_status == "healthy" and env_status == "healthy"
            else "unhealthy"
        )

        return {
            "status": overall_status,
            "service": "weather-ai",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "weather_agent": agent_status,
                "environment": env_status
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "weather-ai",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
