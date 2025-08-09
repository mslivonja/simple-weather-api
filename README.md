# Simple Weather API 

## Python virtual env.

Basic Flask app. - initial project import.

### Create new virtual env and activate

    python3 -n venb .venv
    source .venv/bin/activate

### Install dependencies

    (venv)$ pip install -r requirements.txt

## Run app.

    (venv)$ python -m flask run

    * Debug mode: off
    
    WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
    * Running on http://127.0.0.1:5000
    Press CTRL+C to quit
    127.0.0.1 - - [09/Aug/2025 18:58:08] "GET / HTTP/1.1" 200 -

## REST API - Swagger UI

Access Swagger UI at http://localhost:5000

GET request using following request

    curl -X 'GET' 'http://localhost:5000/weather/Zagreb' \
         -H 'accept: application/json'

### Deactivate virtual env

    (venv)$ deactivate

