import json
import pathlib

import pytest
from unittest.mock import patch, Mock
from weather import WeatherService, WeatherServiceException
from weather import OPENWEATHER_URL

API_KEY = "fake_api_key"

SAMPLE_RESPONSE_PATH="tests/test_data/sample.response.200.json"

@pytest.fixture
def weather_service():
    return WeatherService(api_key=API_KEY)


def fake_response_ok():
    mock_resp = Mock()
    mock_resp.status_code = 200

    file = pathlib.Path(SAMPLE_RESPONSE_PATH)
    with open(file) as f:
        mock_resp.json.return_value = json.load(f)

    return mock_resp


def fake_response_error():
    mock_resp = Mock()
    mock_resp.status_code = 404
    return mock_resp

def test_fetch_weather():
    api_key = None
    with pytest.raises(ValueError):
        WeatherService(api_key)


def test_fetch_weather_url():
    weather_service = WeatherService(api_key=API_KEY)
    with patch('weather.requests.get') as mock_get:
        mock_get.return_value = fake_response_ok()
        # invoke service fetch
        weather_service.fetch_weather('TestCity', 'NL')
        # Ensure requests.get was called exactly once
        mock_get.assert_called_once()
        # Get the call arguments
        called_url = mock_get.call_args[0][0]
        assert called_url == f"{OPENWEATHER_URL}?q=TestCity,NL&appid=fake_api_key&units=metric"


@patch("weather.requests.get")
def test_fetch_weather_success(mock_get, weather_service):
    mock_get.return_value = fake_response_ok()

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


@patch("weather.requests.get")
def test_fetch_weather_failure(mock_get, weather_service):
    mock_get.return_value = fake_response_error()

    with  pytest.raises(WeatherServiceException) as exception_info:
        weather_service.fetch_weather("Nowhere", "UK")

    assert exception_info is not None
    assert exception_info.value.status_code == 404
    assert exception_info.value.city == "Nowhere"
    assert exception_info.value.country_code == "UK"
