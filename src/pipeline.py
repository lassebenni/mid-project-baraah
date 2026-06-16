"""Main pipeline: fetch, validate, transform, store."""

import logging
import os
import sys

from dotenv import load_dotenv


import pandas as pd
import requests
from pydantic import ValidationError

from src.models import WeatherReading
from src.storage import insert_readings, upload_raw_json

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(message)s",
)
logging.getLogger("azure").setLevel(logging.WARNING)
log = logging.getLogger(__name__)


CITIES = {
    "Amsterdam": (52.37, 4.89),
    "Rotterdam": (51.92, 4.48),
    "Utrecht": (52.09, 5.12),
}

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
HOURLY_VARS = "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m"


def fetch_data():
    """Fetch RAW API responses (NO processing)."""
    raw_responses = []

    for city, (lat, lon) in CITIES.items():
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": HOURLY_VARS,
            "timezone": "UTC",
            "forecast_days": 1,
        }

        response = requests.get(OPEN_METEO_URL, params=params, timeout=10)
        response.raise_for_status()

        raw_responses.append({"city": city, "data": response.json()})

    log.info("Fetched RAW data for %d cities", len(raw_responses))
    return raw_responses


# SAVE RAW TO BLOB
def save_raw(raw_data):
    upload_raw_json(raw_data)


# process row to flatten
def process(raw_data):
    """Convert raw API into structured records."""
    #
    records = []

    for item in raw_data:
        city = item["city"]
        hourly = item["data"]["hourly"]

        times = hourly["time"]

        for i, t in enumerate(times):
            records.append(
                {
                    "city": city,
                    "timestamp": t,
                    "temperature": hourly["temperature_2m"][i],
                    "humidity": hourly["relative_humidity_2m"][i],
                    "precipitation": hourly["precipitation"][i],
                    "wind_speed": hourly["wind_speed_10m"][i],
                }
            )

    return records 


# VALIDATION (Pydantic)
def validate(records):
    valid = []

    for r in records:
        try:
            valid.append(WeatherReading(**r))
        except ValidationError as e:
            log.warning("Invalid record skipped: %s", e)

    log.info("Validated %d / %d records", len(valid), len(records))
    return valid


# TRANSFORM (Pandas)
def transform(readings):
    df = pd.DataFrame([r.model_dump() for r in readings])

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["is_raining"] = df["precipitation"] > 0
    df["wind_speed_ms"] = (df["wind_speed"] / 3.6).round(2)

    df = df.dropna(subset=["temperature", "humidity"])

    log.info("Transformed %d rows", len(df))
    return df



def run():
    log.info("Pipeline started")

    raw = fetch_data()

    save_raw(raw)

    records = process(raw)

    readings = validate(records)

    if not readings:
        log.error("No valid data")
        sys.exit(1)

    df = transform(readings)

    insert_readings(df)
    log.info("Pipeline finished successfully (%d rows)", len(df))


if __name__ == "__main__":
    for var in ["POSTGRES_URL", "AZURE_STORAGE_CONNECTION_STRING"]:
        if var not in os.environ:
            log.error("Missing required environment variable: %s", var)
            sys.exit(1)

    run()
