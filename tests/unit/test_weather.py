import json
import pathlib
from typing import Any

import pytest
from unittest.mock import patch, Mock, MagicMock

import requests
from _pytest.monkeypatch import MonkeyPatch
from requests import HTTPError

from weather import WeatherService, WeatherServiceException
from weather import OPENWEATHER_URL

API_KEY = "fake_api_key"

SAMPLE_RESPONSE_PATH="tests/test_data/sample.response.200.json"

def fake_get_error() -> Any:
    class FakeResponse:
        def raise_for_status(self) -> None:
            response = requests.models.Response()
            response.status_code = 404
            http_error = HTTPError(404)
            http_error.response = response
            raise http_error

        def json(self) -> Any: pass

    return FakeResponse()

@pytest.fixture
def mock_requests_get(monkeypatch: MonkeyPatch) -> Any:
    mock_get = MagicMock()
    monkeypatch.setattr(requests, "get", mock_get)
    return mock_get

@pytest.fixture
def fake_get_ok(mock_requests_get):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.status_code = 200

    file_path = pathlib.Path(SAMPLE_RESPONSE_PATH)
    with open(file_path) as f:
        mock_response.json.return_value = json.load(f)

    # Make requests.get() return the mock response
    mock_requests_get.return_value = mock_response

    service = WeatherService(API_KEY)
    return mock_requests_get, service

@pytest.fixture
def fake_get_error(mock_requests_get):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.json.return_value = {"message": "City not found"}

    http_error = HTTPError(404)
    http_error.response = mock_response
    mock_response.raise_for_status.side_effect = http_error

    mock_requests_get.return_value = mock_response

    service = WeatherService(API_KEY)
    return mock_requests_get, service


def test_fetch_weather():
    """
    Test that service creation will fail if API key cannot be resolved
    :return:
    """
    api_key = None
    with pytest.raises(ValueError):
        WeatherService(api_key)


def test_fetch_weather_url(fake_get_ok) -> None:
    """
    Test that request.get was called with appropriate URL
    :return:
    """
    mock_get, service = fake_get_ok
    city = 'TestCity'
    country_code = 'NL'

    # invoke service for 'TestCity:NL'
    # do not care what is returned
    service.fetch_weather('TestCity', 'NL')

    params = {
        "q": f"{city},{country_code}",
        "appid": API_KEY,
        "units": "metric",
    }
    mock_get.assert_called_once_with(OPENWEATHER_URL, params=params)


def test_fetch_weather_success(fake_get_ok) -> None:
    """
    Test that response data is parsed correctly
    :param fake_get_ok Fixture for successful response
    :return:
    """
    mock_get, service = fake_get_ok

    result = service.fetch_weather("TestCity", "UK")

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


def test_fetch_weather_failure(fake_get_error):
    mock_get, service = fake_get_error

    with  pytest.raises(WeatherServiceException) as exception_info:
        service.fetch_weather("Nowhere", "UK")

    assert str(exception_info.value) == "City 'Nowhere':'UK' not found"
