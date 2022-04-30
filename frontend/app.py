import os
import json
import requests
from flask import Flask, render_template
from flask_healthz import healthz
from quotes import default_quotes


# create the flask app
app = Flask(__name__)

# add flask-healthz config to flask config
app.config["HEALTHZ"] = {"live": "healthz.liveness", "ready": "healthz.readiness"}
# create the healthz endpoints
app.register_blueprint(healthz, url_prefix="/healthz")


# host for the backend, if not set default to False
backend_endpoint = os.environ.get("backend_host", False)


def check_if_backend_is_available() -> bool:
    """
    Check if the backend is reachable and should be used
    """

    # check if the env var has been set
    if backend_endpoint:
        # try querying the backend
        try:
            backend_url = f"http://{backend_endpoint}/healthz/ready"
            response = requests.get(backend_url)
            return response.status_code == 200
        except requests.ConnectionError:
            return False
    else:
        return False


@app.route("/")
def index():
    """Main endpoint, serves the frontend"""

    # check if the backend and database are available and communicate this to user
    backend_available = check_if_backend_is_available()
    database_available = False

    # render the html template with arguments
    rendered = render_template(
        "index.html", backend=backend_available, database=database_available, quotes=default_quotes
    )

    return rendered


@app.route("/quotes")
def quotes():
    """Get all available quotes as JSON"""

    if check_if_backend_is_available():
        raise NotImplementedError()
    else:
        return json.dumps(default_quotes)
