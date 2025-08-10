# Simple Weather API 

## Python virtual env.

Basic Flask app. - initial project import.

### Create new virtual env and activate

    python3 -n venb .venv
    source .venv/bin/activate

### Install dependencies

    (venv)$ pip install -r requirements.txt

## Package app.

Package application using docker

    docker build -t simple-weather-api:latest -f Dockerfile .

## Run app.

### Run locally in virtual env.

    (venv)$ python -m flask run

    * Debug mode: off
    
    WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
    * Running on http://127.0.0.1:5000
    Press CTRL+C to quit
    127.0.0.1 - - [09/Aug/2025 18:58:08] "GET / HTTP/1.1" 200 -

### Run in docker container

Run docker container with app. only

    export OPENWEATHER_API_KEY=<api key>
    docker run -d \
        --name simple-weather-api \
        -p 5000:5000 \
        --restart always \
        -e OPENWEATHER_API_KEY=$OPENWEATHER_API_KEY
        simple-weather-api:latest 

    docker logs -f simple-weather-api

    * Debug mode: off
    WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
    * Running on http://127.0.0.1:5000
    Press CTRL+C to quit

Run with docker compose

Prerequisite - create .env file with following variables
    cat .env
    OPENWEATHER_API_KEY=<api key>
    MINIO_ACCESS_KEY=<user>
    MINIO_SECRET_KEY=<secret>

    docker-compose up -d

    docker logs -f simple-weather-api

    docker-compose down

## REST API - Swagger UI

Access Swagger UI at http://localhost:5000/api/docs

GET request using following request

    curl -X 'GET' 'http://localhost:5000/weather/api/city/Zagreb' \
         -H 'accept: application/json'

Response is JSON formatted data.

    curl -X 'GET' 'http://localhost:5000/weather/api/city/Zagreb' \
         -H 'accept: text/csv'

Response is temp. S3 storage URL - file temp download link.


### Deactivate virtual env

    (venv)$ deactivate

