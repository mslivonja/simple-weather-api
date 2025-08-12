import csv
import io
import os
import time
from datetime import datetime

from flask import Flask, request, Response
from flask_restx import Api, Resource, fields, reqparse
from werkzeug.middleware.proxy_fix import ProxyFix
from weather import WeatherService, WeatherServiceException
from s3_storage import S3Service
from db_storage import db, WeatherDBService

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET = os.getenv("S3_BUCKET")

DB_HOSTNAME = os.getenv("DB_HOSTNAME")
DB_PORT = os.getenv("DB_PORT")
DB_USER= os.getenv("DB_USER")
DB_PASSWORD= os.getenv("DB_PASSWORD")
DB_NAME= os.getenv("DB_NAME")

DB_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOSTNAME}:{DB_PORT}/{DB_NAME}"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

app.wsgi_app = ProxyFix(app.wsgi_app)

# Initialize API
api = Api(app,  version='1.0',
          title='Simple Weather API',
          description='Simple Weather API',
          doc='/api/docs'
)

# Setup namespace
weather_ns = api.namespace('weather/api', description='Weather operations')
weather_request_ns = api.namespace('weather/request/api', description='Weather request operations')

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

weather_request = api.model('WeatherRequest', {
    'city': fields.String(required=True, description='The city name'),
    'units': fields.String(required=True, description='Weather metric'),
    'headers': fields.Raw,
    'weather_data': fields.Raw,
    'timestamp': fields.DateTime(required=True, description='Weather request date'),
})

# Weather Service
weather_service = WeatherService(OPENWEATHER_API_KEY)
# S3 storage Service
s3 = S3Service(
        endpoint = S3_ENDPOINT_URL,
        bucket_name= S3_BUCKET,
        access_key= AWS_ACCESS_KEY_ID,
        secret_key= AWS_SECRET_ACCESS_KEY
    )
# DB storage Service
db_service = WeatherDBService(app)
db_service.init_db()

with app.app_context():
    db.create_all()  # <-- create tables on startup, before serving requests

@weather_ns.route('/city/<string:city>')
@weather_ns.response(404, 'Weather data not found')
class WeatherByCity(Resource):
    """Get weather forecast info for given city"""

    @weather_ns.doc(
        params={
            "city": 'City name'
        },
        responses={
            200: "Weather report in JSON or CSV",
            404: "City not found",
            500: "Weather service unavailable"
        }
    )
    @weather_ns.produces(['application/json', 'text/csv'])
    def get(self, city: str):
        """
               Get live weather data for given city
               Fetch  data from OpenWeatherMap API

               **Content negotiation**:
               - `Accept: application/json` → JSON output
               - `Accept: text/csv` → CSV output
               """
        try:
            accept_header = request.headers.get("Accept", "application/json").lower()
            weather_data = weather_service.fetch_weather(city, None)

            # Save request in DB
            db_service.save_request(
                city=city,
                units="metric",
                headers=dict(request.headers),
                weather_data=weather_data
            )

            if "text/csv" in accept_header:
                # Generate CSV in memory
                csv_buffer = io.StringIO()
                writer = csv.DictWriter(csv_buffer, fieldnames=weather_data.keys())
                writer.writeheader()
                writer.writerow(weather_data)
                csv_buffer.seek(0)

                # Upload to S3
                file_name = f"weather_{city.lower().replace(' ', '_')}_{int(time.time())}.csv"
                s3_url = s3.upload_file(csv_buffer.getvalue(), file_name)

                return Response(s3_url, mimetype='text/csv')

            # call marshall manually only if output is JSON
            return weather_ns.marshal(weather_data, weather)
        except WeatherServiceException as e:
            # catch weather service exception
            if e.status_code == 404:
                api.abort(404, f'Unknown city {city}')
            else:
                api.abort(500, f'Unexpected Error while fetching weather data for city {city}', {str(e)})
        except Exception as e:
            # catch all other exceptions
            api.abort(500, f"Unexpected Error, GET weather data for city '{city}', {str(e)}")


# Define request parser
parser = reqparse.RequestParser()
parser.add_argument(
    "request_date",
    type=str,
    required=True,
    help="Weather request date in YYYY-MM-DD format"
)

@weather_request_ns.route('/')
class WeatherRequest(Resource):
    """Get weather request"""

    @weather_request_ns.produces(['application/json'])
    @weather_request_ns.marshal_with(weather_request)
    @weather_request_ns.expect(parser)
    def get(self):
        args = parser.parse_args()
        reqs_date_str = args["request_date"]
        req_date = datetime.strptime(reqs_date_str, "%Y-%m-%d")
        reqs = db_service.get_request_by_date(req_date)
        dict_reqs = [r.to_dict() for r in reqs]
        return dict_reqs

if __name__ == '__main__':
    app.run()
