"""
Frontend flask app, serves the graphical html version
and provides endpoints for getting/pushing quotes.
"""
import os
import random
import requests
from flask import Flask, render_template, jsonify, request
from flask_healthz import healthz
from quotes import default_quotes


# create the flask app
app = Flask(__name__)

# test logging
app.logger.info("info")
app.logger.warning("warning")
app.logger.debug("debug")
app.logger.error("error")
app.logger.critical("critical")

# add flask-healthz config to flask config
app.config["HEALTHZ"] = {"live": "healthz.liveness", "ready": "healthz.readiness"}
# create the healthz endpoints
app.register_blueprint(healthz, url_prefix="/healthz")


# host for the backend, if not set default to False
BACKEND_ENDPOINT = os.environ.get("backend_host", False)
# build the url for the backend
BACKEND_URL = f"http://{BACKEND_ENDPOINT}"


def check_backend_endpoint_env_var() -> bool:
    """Checks if the user has set the backend host environment variable"""
    if BACKEND_ENDPOINT:
        print(
            f"Found 'backend_host' environment variable, will attempt to connect to the backend on: {BACKEND_URL}",
            flush=True,
        )
        return True
    print("WARNING: 'backend_host' environment variable not set, set this to connect to the backend.", flush=True)
    return False


def check_if_database_is_available() -> bool:
    """Check if the database is reachable and should be used"""
    # check if the env var has been set
    if check_backend_endpoint_env_var():
        # try querying the backend
        try:
            backend_health_endpoint = f"{BACKEND_URL}/check-db-connection"
            response = requests.get(backend_health_endpoint)
            if response.status_code == 200:
                body = response.json()
                if "db-connected" in body:
                    if body["db-connected"] == "true":
                        return True
                    return False
            else:
                return False
            return False
        except (requests.ConnectionError, KeyError):
            return False
    else:
        return False


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


def get_random_quote_from_backend() -> str:
    """get a single quote from the backend"""
    response = requests.get(f"{BACKEND_URL}/quote")
    if response.status_code == 200:
        return response.text
    # TODO propper logging
    print("Error: did not get a response 200 from backend", flush=True)
    return ""


def get_all_quotes_from_backend() -> list[str]:
    """get list of all quotes form the backend"""
    response = requests.get(f"{BACKEND_URL}/quotes")
    if response.status_code == 200:
        return response.json()
    # TODO propper logging
    print("Error: did not get a response 200 from backend")
    return []


@app.route("/")
def index():
    """Main endpoint, serves the frontend"""
    # check if the backend and database are available and communicate this to user
    backend_available = check_if_backend_is_available()
    # check if the backend is communicating with the database
    database_available = check_if_database_is_available()

    if backend_available:
        _quotes = get_all_quotes_from_backend()
    else:
        _quotes = default_quotes

    # render the html template with arguments
    return render_template("index.html", backend=backend_available, database=database_available, quotes=_quotes)


@app.route("/random-quote")
def random_quote():
    """return a random quote"""
    if check_if_backend_is_available():
        #  return random.choice(get_all_quotes_from_backend())
        return get_random_quote_from_backend()
    return random.choice(default_quotes)


@app.route("/quotes")
def quotes():
    """Get all available quotes as JSON"""
    if check_if_backend_is_available():
        return jsonify(get_all_quotes_from_backend())
    return jsonify(default_quotes)


@app.route("/add-quote", methods=["POST"])
def add_quote():
    """receive quote and pass it on to the backend"""
    if request.method == "POST":
        request_json = request.get_json()
        print(request_json, flush=True)

        if "quote" in request_json:
            url = f"{BACKEND_URL}/add-quote"
            requests.post(url, json=request_json)
        else:
            # TODO propper logging
            print("Error: could not find 'quote' in request", flush=True)
            return "No 'quote' key in JSON", 500

        return "Quote received", 200
    return "Could not parse quote", 500
