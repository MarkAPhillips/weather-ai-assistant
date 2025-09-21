from pydantic import BaseModel
from typing import Optional, List


class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: str
    message_id: str


class ChatSession(BaseModel):
    session_id: str
    messages: List[ChatMessage]
    created_at: str
    last_activity: str


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    message_id: str
    timestamp: str


class AirQualityData(BaseModel):
    aqi: Optional[int] = None
    pm25: Optional[float] = None
    pm10: Optional[float] = None
    o3: Optional[float] = None
    no2: Optional[float] = None
    so2: Optional[float] = None
    co: Optional[float] = None
    location: Optional[str] = None
    timestamp: Optional[str] = None
    health_recommendations: Optional[List[str]] = None


class WeatherDataWithAirQuality(BaseModel):
    city: str
    country: str
    temperature: int
    condition: str
    humidity: int
    wind_speed: float
    wind_direction: str
    pressure: int
    visibility: int
    uv_index: Optional[int] = None
    air_quality: Optional[AirQualityData] = None


ChatMessage.model_rebuild()
ChatSession.model_rebuild()
ChatRequest.model_rebuild()
ChatResponse.model_rebuild()
AirQualityData.model_rebuild()
WeatherDataWithAirQuality.model_rebuild()
