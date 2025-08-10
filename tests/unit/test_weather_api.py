import io

import pytest
from unittest.mock import patch
from tests.unit.test_weather import API_KEY


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv('OPENWEATHER_API_KEY', API_KEY)
    from app import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Fake Weather data returned from Weather service
fake_weather_data = {
  "city": "Zagreb",
  "location": "Donji grad",
  "temp": 33.83,
  "feels_like": 35.65,
  "temp_min": 31.82,
  "temp_max": 33.83,
  "pressure": 1020,
  "humidity": 42,
  "visibility": 10000,
  "wind_speed": 0,
  "description": "Clear sky",
  "timestamp": '2025-08-09T23:49:58'
}


@patch('app.WeatherService.fetch_weather')
def test_get_weather_json(mock_fetch, client):
    mock_fetch.return_value = fake_weather_data

    response = client.get('/weather/api/city/Zagreb', headers={"Accept": "application/json"})
    assert response.status_code == 200
    assert response.is_json
    json_data = response.get_json()
    assert json_data == fake_weather_data
    assert json_data["location"] == "Donji grad"

@patch('app.S3Service.upload_file')
@patch('app.WeatherService.fetch_weather')
def test_get_weather_csv(mock_fetch, mock_s3, client):
    mock_fetch.return_value = fake_weather_data
    mock_s3.return_value = "http://localhost:9000/tmp"
    response = client.get('/weather/api/city/Zagreb', headers={"Accept": "text/csv"})
    assert response.status_code == 200
    assert response.data.decode("utf-8") == "http://localhost:9000/tmp"
