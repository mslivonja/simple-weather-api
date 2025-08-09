from flask import Flask
from flask_restx import Api, Resource, fields
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app,  version='1.0', title='Simple Weather API',
                description='Simple Weather API',
)

ns = api.namespace('weather', description='Weather operations')

weather = api.model('Weather', {
    'id': fields.Integer(readonly=True, description='The weather data unique identifier'),
    'city': fields.String(required=True, description='The city name')
})


@ns.route('/<string:city>')
@ns.response(404, 'Weather data not found')
@ns.param('city', 'City name')
class WeatherByCity(Resource):
    """Show a single weather info item for given city"""

    @ns.doc('Get weather data for given city name')
    @ns.marshal_with(weather)
    def get(self, city: str):
        """Fetch a given resource"""
        return {
            'id': 1,
            'city': city
        }


if __name__ == '__main__':
    app.run()
