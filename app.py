import os

from flask import Flask
from flask_restx import Api, Resource, fields
from werkzeug.middleware.proxy_fix import ProxyFix
from weather import WeatherService, WeatherServiceException

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

# Initialize API
api = Api(app,  version='1.0',
          title='Simple Weather API',
          description='Simple Weather API',
)

# Setup namespace
ns = api.namespace('weather', description='Weather operations')

# Setup model
weather = api.model('Weather', {
    'city': fields.String(required=True, description='The city name'),
    'location': fields.String(required=True, description='Location name within city'),
    'temp': fields.Float(required=True, description='Temperature'),
    'feels_like': fields.Float(required=True, description='Feels like temperature'),
    'temp_min': fields.Float(required=True, description='Min. temperature'),
    'temp_max': fields.Float(required=True, description='Max. temperature'),
    'pressure': fields.Integer(required=True, description='Pressure'),
    'humidity': fields.Integer(required=True, description='Humidity'),
    'visibility': fields.Integer(required=True, description='Visibility'),
    'wind_speed': fields.Integer(required=True, description='Wind speed'),
    'description': fields.String(required=True, description='Weather description'),
    'timestamp': fields.DateTime(required=True, description='Weather forecast date')
})

weather_service = WeatherService(OPENWEATHER_API_KEY)

@ns.route('/<string:city>')
@ns.response(404, 'Weather data not found')
@ns.param('city', 'City name')
class WeatherByCity(Resource):
    """Get weather forecast info for given city"""

    @ns.doc('Get weather forecast data for given city name')
    @ns.marshal_with(weather)
    def get(self, city: str):
        """ Get weather info for given city, fetch data from OpenWeatherMap"""
        try:
            return weather_service.fetch_weather(city, None)
        except WeatherServiceException as e:
            # catch weather service exception
            if e.status_code == 404:
                api.abort(404, f'Unknown city {city}')
            else:
                api.abort(500, f'Unexpected Error while fetching weather data for city {city}', {str(e)})
        except Exception as e:
            # catch all other exceptions
            api.abort(500, f"Unexpected Error, GET weather data for city '{city}', {str(e)}")


if __name__ == '__main__':
    app.run()
