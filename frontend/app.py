import os
import json
import requests
from flask import Flask, render_template, jsonify, request
from flask_healthz import healthz
from quotes import default_quotes


# create the flask app
app = Flask(__name__)

# add flask-healthz config to flask config
app.config["HEALTHZ"] = {"live": "healthz.liveness", "ready": "healthz.readiness"}
# create the healthz endpoints
app.register_blueprint(healthz, url_prefix="/healthz")


# host for the backend, if not set default to False
BACKEND_ENDPOINT = os.environ.get("backend_host", False)
# build the url for the backend
BACKEND_URL = f"http://{BACKEND_ENDPOINT}"


def check_if_backend_is_available() -> bool:
    """Check if the backend is reachable and should be used"""
    # check if the env var has been set
    if BACKEND_ENDPOINT:
        # try querying the backend
        try:
            backend_health_endpoint = f"{BACKEND_URL}/healthz/ready"
            response = requests.get(backend_health_endpoint)
            return response.status_code == 200
        except requests.ConnectionError:
            return False
    else:
        return False


def get_quote() -> str:
    """get a single quote from the backend"""
    response = requests.get(f"{BACKEND_URL}/quote")
    if response.status_code == 200:
        return response.body
    else:
        # TODO propper logging
        print("Error: did not get a response 200 from backend", flush=True)
        return ""


def get_quotes() -> list[str]:
    """get list of all quotes form the backend"""
    response = requests.get(f"{BACKEND_URL}/quotes")
    if response.status_code == 200:
        return response.json()
    else:
        # TODO propper logging
        print("Error: did not get a response 200 from backend")
        return []


@app.route("/")
def index():
    """Main endpoint, serves the frontend"""
    # check if the backend and database are available and communicate this to user
    backend_available = check_if_backend_is_available()
    # TODO
    database_available = False

    if backend_available:
        quotes = get_quotes()
    else:
        quotes = default_quotes

    # render the html template with arguments
    return render_template("index.html", backend=backend_available, database=database_available, quotes=quotes)


@app.route("/quotes")
def quotes():
    """Get all available quotes as JSON"""
    if check_if_backend_is_available():
        return jsonify(get_quotes())
    return jsonify(default_quotes)


@app.route("/add-quote", methods=["POST"])
def add_quote():
    """receive quote and pass it on to the backend"""
    if request.method == "POST":
        request_json = request.get_json()
        print(request_json, flush=True)

        if "quote" in request_json:
            url = f"{BACKEND_URL}/add-quote"
            # TODO fix
            requests.post(url, data=request_json)
        else:
            # TODO propper logging
            print("Error: could not find 'quote' in request", flush=True)
            return "No 'quote' key in JSON", 500

        return "Quote received", 200
    return "Could not parse quote", 500
