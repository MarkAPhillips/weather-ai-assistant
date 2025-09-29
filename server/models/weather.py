from pydantic import BaseModel
from typing import Optional
from air_quality import AirQualityData


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


WeatherDataWithAirQuality.model_rebuild()