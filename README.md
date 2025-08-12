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

    # Weather service config
    OPENWEATHER_API_KEY=<api key>

    # Minio config 
    MINIO_ACCESS_KEY=<user>
    MINIO_SECRET_KEY=<secret>

    # S3 storage service config
    S3_ENDPOINT_URL=http://localhost:9000
    AWS_ACCESS_KEY_ID=myminioadmin
    AWS_SECRET_ACCESS_KEY=myminiosecret
    S3_BUCKET=test

    # DB config
    DB_USER=mypostgresadmin
    DB_PASSWORD=myposgressecret
    DB_NAME=weather

    # PG Admin config
    PG_ADMIN_MAIL=mypgadmin@gmail.com
    PG_ADMIN_PASSWORD=mypgadminsecret


    docker-compose up -d

    docker logs -f simple-weather-api

    docker-compose down

## Minio S3 Storage

S3 interface: http://localhost:9000
Browser UI: http://localhost:9001

Note: App. assumes bucket already exists. Connect to Minio browser UI at h
http://localhost:9001 and create bucket='test' manually.

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

