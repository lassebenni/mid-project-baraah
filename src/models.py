"""Pydantic models for data validation."""

from pydantic import BaseModel, Field


class WeatherReading(BaseModel):
    """A single hourly weather reading for one city."""

    city: str
    timestamp: str
    temperature: float = Field(ge=-50, le=50)
    humidity: float = Field(ge=0, le=100)
    precipitation: float = Field(ge=0, le=500)
    wind_speed: float = Field(ge=0, le=250)
