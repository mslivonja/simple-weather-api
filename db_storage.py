from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

from sqlalchemy import func

db = SQLAlchemy()

# Data model
class WeatherRequest(db.Model):

    __tablename__ = "weather_requests"

    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100))
    units = db.Column(db.String(20))
    headers = db.Column(db.Text)  # stored as JSON
    weather_data = db.Column(db.Text)  # stored as JSON
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "city": self.city,
            "units": self.units,
            "headers": json.loads(self.headers),
            "weather_data": json.loads(self.weather_data),
            "timestamp": self.timestamp.isoformat()
        }

# DB service
class WeatherDBService:
    """Service for persisting and retrieving weather request data."""

    def __init__(self, app: Flask):
        self.app = app

    def init_db(self):
        with self.app.app_context():
            db.create_all()

    def save_request(self, city, units, headers, weather_data):
        record = WeatherRequest(
            city=city,
            units=units,
            headers=json.dumps(headers),
            weather_data=json.dumps(weather_data, default=str),
            timestamp=datetime.utcnow()
        )
        db.session.add(record)
        db.session.commit()
        return record

    def get_all_requests(self):
        return WeatherRequest.query.order_by(WeatherRequest.timestamp.desc()).all()

    def get_request_by_id(self, request_id):
        return WeatherRequest.query.get(request_id)

    def get_request_by_date(self, request_date):
        return WeatherRequest.query.filter(
                func.date(WeatherRequest.timestamp) == func.date(request_date)
            ).all()
