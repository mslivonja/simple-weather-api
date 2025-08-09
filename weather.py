import os
from datetime import datetime
import requests

OPENWEATHER_URL = 'http://api.openweathermap.org/data/2.5/weather'

class WeatherService:
    def __init__(self, api_key: str | None , units: str = "metric"):
        self.api_key = os.environ.get('OPENWEATHER_API_KEY')
        if api_key:
            # Override, set explicitly in app.
            self.api_key = api_key
        if api_key is None:
            raise ValueError("API key is required")

        self.units = units

    def fetch_weather(self, city: str, country_code: str):
        """Fetch live weather data from OpenWeatherMap API."""
        url = (
            f"{ OPENWEATHER_URL }"
            f"?q={city},{country_code}&appid={self.api_key}&units={self.units}"
        )
        response = requests.get(url)
        if response.status_code != 200:
            raise WeatherServiceException(response.status_code,
                                          city,
                                          country_code)

        data = response.json()
        return {
            "city": city,
            "location": data["name"],
            "temp": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "temp_min": data["main"]["temp_min"],
            "temp_max": data["main"]["temp_max"],
            "pressure": data["main"]["pressure"],
            "humidity": data["main"]["humidity"],
            "visibility": data["visibility"],
            "wind_speed": data["wind"]["speed"],
            "description": data["weather"][0]["description"].capitalize(),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

class WeatherServiceException(Exception):
    def __init__(self, status_code:int, city:str, country_code:str):
        self.status_code = status_code
        self.city = city
        self.country_code = country_code

    def __str__(self):
        return f"Request for City: '{self.city}', Country: '{self.country_code}' failed with status code {self.status_code}"