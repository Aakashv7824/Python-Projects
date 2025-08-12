
#!/usr/bin/env python3
"""
Weather Fetcher & Saver (Beginner-Friendly)

- Input: city name (e.g., "Mumbai", "London, UK")
- Output: prints current weather & appends a row to weather_log.csv
- APIs: Open-Meteo (no API key needed)
"""

import csv
import datetime as dt
import sys
from pathlib import Path
from typing import Optional, Tuple

import requests

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
CSV_PATH = Path("weather_log.csv")


def geocode_city(city: str) -> Optional[Tuple[float, float, str]]:
    """
    Returns (lat, lon, resolved_name) or None if not found.
    Uses Open-Meteo geocoding (free, no key).
    """
    resp = requests.get(GEO_URL, params={"name": city, "count": 1, "language": "en"}, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    results = data.get("results") or []
    if not results:
        return None
    r = results[0]
    resolved = f"{r.get('name','?')}, {r.get('country','?')}"
    return float(r["latitude"]), float(r["longitude"]), resolved


def fetch_weather(lat: float, lon: float) -> dict:
    """
    Fetch current weather for a lat/lon. Returns JSON dict.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "weather_code"],
        "timezone": "auto",
    }
    resp = requests.get(WEATHER_URL, params=params, timeout=20)
    resp.raise_for_status()
    return resp.json()


def decode_weather_code(code: int) -> str:
    """
    Maps Open-Meteo weather_code to a short description.
    Ref: https://open-meteo.com/en/docs (common subset)
    """
    mapping = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        80: "Rain showers (slight)",
        81: "Rain showers (moderate)",
        82: "Rain showers (violent)",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail",
    }
    return mapping.get(int(code), f"Unknown ({code})")


def save_to_csv(row: dict, path: Path = CSV_PATH) -> None:
    """
    Appends a record to CSV, creating it with a header if it doesn't exist.
    """
    new_file = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "timestamp_local",
                "city",
                "lat",
                "lon",
                "temperature_c",
                "humidity_pct",
                "wind_kmh",
                "condition",
            ],
        )
        if new_file:
            writer.writeheader()
        writer.writerow(row)


def main() -> int:
    print("=== Weather Fetcher & Saver ===")
    if len(sys.argv) > 1:
        city = " ".join(sys.argv[1:])
    else:
        city = input("Enter a city (e.g., 'Mumbai', 'London, UK'): ").strip()

    if not city:
        print("No city provided. Exiting.")
        return 1

    try:
        g = geocode_city(city)
        if not g:
            print(f"Could not find location for '{city}'. Try a more specific name.")
            return 2

        lat, lon, resolved_name = g
        w = fetch_weather(lat, lon)
        cur = w.get("current", {})
        temp = cur.get("temperature_2m")
        hum = cur.get("relative_humidity_2m")
        wind = cur.get("wind_speed_10m")
        code = cur.get("weather_code")
        condition = decode_weather_code(code) if code is not None else "Unknown"

        # Print a friendly summary
        print(f"\nWeather in {resolved_name}:")
        print(f"  Temperature: {temp} °C")
        print(f"  Humidity:    {hum} %")
        print(f"  Wind:        {wind} km/h")
        print(f"  Condition:   {condition}")

        # Save a log row
        import datetime as dt
        now_local = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_to_csv(
            {
                "timestamp_local": now_local,
                "city": resolved_name,
                "lat": f"{lat:.4f}",
                "lon": f"{lon:.4f}",
                "temperature_c": temp,
                "humidity_pct": hum,
                "wind_kmh": wind,
                "condition": condition,
            }
        )
        print(f"\nSaved to {CSV_PATH.resolve()}")
        return 0

    except requests.HTTPError as e:
        print(f"HTTP error: {e} (check your internet or try again later)")
        return 3
    except requests.RequestException as e:
        print(f"Network error: {e}")
        return 4
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 5


if __name__ == "__main__":
    raise SystemExit(main())
