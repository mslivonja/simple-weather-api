import json
import pathlib
from typing import Any

import pytest
from unittest.mock import patch, Mock

import requests
from requests import HTTPError

from weather import WeatherService, WeatherServiceException
from weather import OPENWEATHER_URL

API_KEY = "fake_api_key"

SAMPLE_RESPONSE_PATH="tests/test_data/sample.response.200.json"

@pytest.fixture
def weather_service():
    return WeatherService(api_key=API_KEY)


def fake_response_ok(url:str, params: dict[str, Any] = None) -> Any:
    class FakeResponse:
        def raise_for_status(self) -> None:pass
        def json(self) -> Any:
            file_path = pathlib.Path(SAMPLE_RESPONSE_PATH)
            with open(file_path) as f:
                return json.load(f)

    return FakeResponse()


def fake_response_error(url:str, params: dict[str, Any] = None):
    class FakeResponse:
        def raise_for_status(self) -> None:
            response = requests.models.Response()
            response.status_code = 404
            http_error = HTTPError(404)
            http_error.response = response
            raise http_error
        def json(self) -> Any: pass

    return FakeResponse()

def test_fetch_weather():
    """
    Test that service creation will fail if API key cannot be resolved
    :return:
    """
    api_key = None
    with pytest.raises(ValueError):
        WeatherService(api_key)


def test_fetch_weather_url(monkeypatch: pytest.MonkeyPatch):
    """
    Test that request.get was call with appropriate URL
    :return:
    """
    monkeypatch.setattr( "weather.requests.get", fake_response_ok)
    weather_service = WeatherService(api_key=API_KEY)

    weather_service.fetch_weather('TestCity', 'NL')


def test_fetch_weather_success(monkeypatch: pytest.MonkeyPatch):
    """
    Test that response data is parsed correctly
    :param mock_get:
    :param weather_service:
    :return:
    """
    monkeypatch.setattr("weather.requests.get", fake_response_ok)
    weather_service = WeatherService(api_key=API_KEY)

    result = weather_service.fetch_weather("TestCity", "UK")

    assert result is not None
    # noinspection SpellCheckingInspection
    assert result["location"] == "Donji grad"
    assert result["temp"] == 24.94
    assert result["temp_min"] == 20.82
    assert result["temp_max"] == 24.94
    assert result["pressure"] == 1020
    assert result["humidity"] == 59
    assert result["visibility"] == 10000
    assert result["description"] == "Clear sky"
    assert "timestamp" in result  # Date string exists
    assert result["timestamp"].isoformat() == "2025-08-09T23:49:58"


def test_fetch_weather_failure(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("weather.requests.get", fake_response_error)
    weather_service = WeatherService(api_key=API_KEY)

    with  pytest.raises(WeatherServiceException) as exception_info:
        weather_service.fetch_weather("Nowhere", "UK")

    assert str(exception_info.value) == "City 'Nowhere':'UK' not found"
