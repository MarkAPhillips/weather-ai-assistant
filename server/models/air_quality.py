from pydantic import BaseModel
from typing import Optional, List


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


AirQualityData.model_rebuild()
