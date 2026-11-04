"""Weather Information Tools using OpenWeatherMap API."""

import logging
from collections import defaultdict
from datetime import datetime
from typing import Optional

import httpx

from config.settings import (
    OPENWEATHER_API_KEY,
    WEATHER_BASE_URL,
    WEATHER_GEO_URL,
)

logger = logging.getLogger("weather_tools")


def _geocode_location(location: str) -> Optional[dict]:
    """Helper to resolve city/region names to accurate latitude and longitude."""
    try:
        url = f"{WEATHER_GEO_URL}?q={location.strip()}&limit=1&appid={OPENWEATHER_API_KEY}"
        with httpx.Client(verify=False, timeout=10.0) as client:
            resp = client.get(url)
            if resp.status_code == 200:
                results = resp.json()
                if results and isinstance(results, list) and len(results) > 0:
                    return results[0]
    except Exception as e:
        logger.warning(f"Geocoding lookup failed for '{location}': {e}")
    return None


def get_current_weather(location: str) -> str:
    """Get live current weather conditions for a specific city or location (e.g. 'Midnapore', 'Kolkata', 'Delhi', 'London').
    
    Returns temperature in Celsius, feels-like temperature, humidity, wind speed, and sky conditions.
    """
    loc = location.strip()
    if not loc:
        return "Please specify a location to get the weather for."

    if not OPENWEATHER_API_KEY:
        return "OpenWeatherMap API key is not configured. Please set OPENWEATHER_API_KEY in your .env file."

    try:
        geo = _geocode_location(loc)
        with httpx.Client(verify=False, timeout=10.0) as client:
            if geo:
                lat = geo["lat"]
                lon = geo["lon"]
                name = geo.get("name", loc)
                state = geo.get("state", "")
                country = geo.get("country", "")
                loc_label = f"{name}" + (f", {state}" if state else "") + (f", {country}" if country else "")
                weather_url = f"{WEATHER_BASE_URL}/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
            else:
                loc_label = loc
                weather_url = f"{WEATHER_BASE_URL}/weather?q={loc}&appid={OPENWEATHER_API_KEY}&units=metric"

            resp = client.get(weather_url)
            data = resp.json()

            if resp.status_code != 200 or str(data.get("cod")) != "200":
                msg = data.get("message", "Location not found.")
                return f"Could not retrieve weather for '{location}': {msg}"

            main = data.get("main", {})
            temp = main.get("temp")
            feels_like = main.get("feels_like")
            humidity = main.get("humidity")
            weather_list = data.get("weather", [])
            description = weather_list[0].get("description", "clear") if weather_list else "clear"
            wind_speed = data.get("wind", {}).get("speed", 0)

            return (
                f"Current weather in {loc_label}:\n"
                f"• Condition: {description.capitalize()}\n"
                f"• Temperature: {temp}°C (feels like {feels_like}°C)\n"
                f"• Humidity: {humidity}%\n"
                f"• Wind Speed: {wind_speed} m/s"
            )
    except Exception as e:
        logger.error(f"Error fetching current weather for {location}: {e}", exc_info=True)
        return f"Error retrieving weather for {location}: {str(e)}"


def get_weather_forecast(location: str, days: int = 3) -> str:
    """Get upcoming weather forecast (e.g. for tomorrow or the next 2-5 days) for a city or location.
    
    Useful for questions like 'What is the weather in Midnapore tomorrow?' or 'Will it rain tomorrow in Kolkata?'.
    """
    loc = location.strip()
    if not loc:
        return "Please specify a location to get the forecast for."

    if not OPENWEATHER_API_KEY:
        return "OpenWeatherMap API key is not configured. Please set OPENWEATHER_API_KEY in your .env file."

    # Clamp days between 1 and 5 (standard 5-day forecast)
    days = max(1, min(days, 5))

    try:
        geo = _geocode_location(loc)
        with httpx.Client(verify=False, timeout=10.0) as client:
            if geo:
                lat = geo["lat"]
                lon = geo["lon"]
                name = geo.get("name", loc)
                state = geo.get("state", "")
                country = geo.get("country", "")
                loc_label = f"{name}" + (f", {state}" if state else "") + (f", {country}" if country else "")
                forecast_url = f"{WEATHER_BASE_URL}/forecast?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
            else:
                loc_label = loc
                forecast_url = f"{WEATHER_BASE_URL}/forecast?q={loc}&appid={OPENWEATHER_API_KEY}&units=metric"

            resp = client.get(forecast_url)
            data = resp.json()

            if resp.status_code != 200 or str(data.get("cod")) != "200":
                msg = data.get("message", "Location not found.")
                return f"Could not retrieve forecast for '{location}': {msg}"

            daily_items = defaultdict(list)
            for entry in data.get("list", []):
                dt_txt = entry.get("dt_txt", "")  # e.g., '2026-10-31 12:00:00'
                if dt_txt:
                    day_key = dt_txt.split(" ")[0]
                    daily_items[day_key].append(entry)

            today_str = datetime.now().strftime("%Y-%m-%d")
            forecast_lines = []
            count = 0

            for day_key, entries in daily_items.items():
                if count >= days:
                    break

                temps = [e["main"]["temp"] for e in entries if "main" in e and "temp" in e["main"]]
                descs = [e["weather"][0]["description"] for e in entries if "weather" in e and e["weather"]]
                common_desc = max(set(descs), key=descs.count) if descs else "clear"
                min_temp = round(min(temps), 1) if temps else "N/A"
                max_temp = round(max(temps), 1) if temps else "N/A"

                if day_key == today_str:
                    day_label = f"Today ({day_key})"
                else:
                    try:
                        d_obj = datetime.strptime(day_key, "%Y-%m-%d")
                        day_label = d_obj.strftime("%A (%b %d)")
                    except Exception:
                        day_label = day_key

                forecast_lines.append(f"• {day_label}: {common_desc.capitalize()}, Temp: {min_temp}°C to {max_temp}°C")
                count += 1

            return f"Weather forecast for {loc_label}:\n" + "\n".join(forecast_lines)
    except Exception as e:
        logger.error(f"Error fetching weather forecast for {location}: {e}", exc_info=True)
        return f"Error retrieving forecast for {location}: {str(e)}"
