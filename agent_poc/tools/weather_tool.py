import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import sys
sys.path.insert(0, '..')
from schemas import WebSearchResult


def get_weather(city: str) -> WebSearchResult:
    # 1. First we need coordinates. We'll use open-meteo's geocoding API (free)
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        import requests
        geo_res = requests.get(geo_url).json()
        
        if not geo_res.get("results"):
            return None
            
        lat = geo_res["results"][0]["latitude"]
        lon = geo_res["results"][0]["longitude"]
        name = geo_res["results"][0]["name"]
        country = geo_res["results"][0]["country"]
        
        # 2. Get Weather
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)
        
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "precipitation", "weather_code"]
        }
        
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]
        
        current = response.Current()
        current_temp = current.Variables(0).Value()
        current_humidity = current.Variables(1).Value()
        current_apparent = current.Variables(2).Value()
        
        snippet = f"Location: {name}, {country}\n"
        snippet += f"Temperature: {current_temp:.1f}°C\n"
        snippet += f"Feels Like: {current_apparent:.1f}°C\n"
        snippet += f"Humidity: {current_humidity:.1f}%\n"
        
        return WebSearchResult(
            title=f"Current Weather in {name}",
            snippet=snippet,
            url="https://open-meteo.com/"
        )
        
    except Exception as e:
        return None
        
    return None
