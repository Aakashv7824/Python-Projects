
# Weather Fetcher & Saver

A tiny Python script that fetches current weather for a city using the free Open‑Meteo API (no API key required) and appends the result to `weather_log.csv`.

## Features
- City → Geocode → Current weather (temperature, humidity, wind, condition)
- Friendly console output
- Auto-creates and appends to `weather_log.csv`

## Quick Start
```bash
pip install -r requirements.txt
python weather_fetcher.py "London, UK"
# or:
python weather_fetcher.py
```
Then type a city when prompted.

## Example Output
```
Weather in London, United Kingdom:
  Temperature: 18.3 °C
  Humidity:    60 %
  Wind:        12.0 km/h
  Condition:   Mainly clear

Saved to /path/to/weather_log.csv
```

## Files
- `weather_fetcher.py` — main script
- `weather_log.csv` — created on first run; accumulates results

## Extend
- Add a 5-day forecast
- Plot temperature history from `weather_log.csv` (matplotlib)
- Add `--units` flag (metric/imperial)
