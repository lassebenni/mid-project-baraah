"""Tests for the WeatherReading Pydantic model."""

import pytest
from pydantic import ValidationError

from src.models import WeatherReading


def test_weather_reading_accepts_valid_data():
    """A record with valid values should be accepted as-is."""
    reading = WeatherReading(
        city="Amsterdam",
        timestamp="2026-06-14T00:00",
        temperature=15.1,
        humidity=70.0,
        precipitation=0.0,
        wind_speed=11.5,
    )

    assert reading.city == "Amsterdam"
    assert reading.temperature == 15.1
    assert reading.precipitation == 0.0


def test_weather_reading_rejects_temperature_out_of_range():
    """Temperature above the allowed range (50°C) should raise an error."""
    with pytest.raises(ValidationError):
        WeatherReading(
            city="Amsterdam",
            timestamp="2026-06-14T00:00",
            temperature=999,
            humidity=70.0,
            precipitation=0.0,
            wind_speed=11.5,
        )


def test_weather_reading_rejects_humidity_out_of_range():
    """Humidity above 100% should raise an error."""
    with pytest.raises(ValidationError):
        WeatherReading(
            city="Amsterdam",
            timestamp="2026-06-14T00:00",
            temperature=15.1,
            humidity=150.0,
            precipitation=0.0,
            wind_speed=11.5,
        )


def test_weather_reading_rejects_negative_precipitation():
    with pytest.raises(ValidationError):
        WeatherReading(
            city="Amsterdam",
            timestamp="2026-06-14T00:00",
            temperature=15.0,
            humidity=70.0,
            precipitation=-1.0,
            wind_speed=11.5,
        )


def test_weather_reading_rejects_negative_wind_speed():
    with pytest.raises(ValidationError):
        WeatherReading(
            city="Amsterdam",
            timestamp="2026-06-14T00:00",
            temperature=15.0,
            humidity=70.0,
            precipitation=0.0,
            wind_speed=-10.0,
        )
