import os
from datetime import datetime
import requests
from requests import HTTPError

# noinspection HttpUrlsUsage
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

    def fetch_weather(self, city: str, country_code: str | None):
        """Fetch live weather data from OpenWeatherMap API."""

        try:
            params = {
                "q": f"{city},{country_code}",
                "appid": self.api_key,
                "units": self.units
            }
            response = requests.get(OPENWEATHER_URL, params=params)

            # raise HTTPError
            response.raise_for_status()

            # convert response to JSON
            data = response.json()

            # extract all relevant information from response
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
                "timestamp": datetime.fromtimestamp(data["dt"])
            }
        except Exception as e:
            raise WeatherServiceException(e, city, country_code)

class WeatherServiceException(Exception):

    def __init__(self, e: Exception, city:str, country_code=None):
        self.exception = e
        self.city = city
        self.country_code = country_code

    def __str__(self):
        if  isinstance(self.exception, HTTPError):
            http_error : HTTPError = self.exception
            if http_error.response.status_code == 404:
                return f"City '{self.city}':'{self.country_code}' not found"
            else:
                return (f"HTTP request for city: '{self.city}' "
                        f"and  country '{self.country_code}' "
                        f"failed with status code '{http_error.status_code}'")
        # in all other cases
        return (f"Unknow error occurred while fetching weather from OpenWeatherMap "
                    f"for city '{self.city}' "
                    f"and country code '{self.country_code}'")

