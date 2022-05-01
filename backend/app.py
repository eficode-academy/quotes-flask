import json
import random
from flask import Flask, jsonify, request
from flask_healthz import healthz
from quotes import default_quotes


# create the flask app
app = Flask(__name__)

# add flask-healthz config to flask config
app.config["HEALTHZ"] = {"live": "healthz.liveness", "ready": "healthz.readiness"}
# create the healthz endpoints
app.register_blueprint(healthz, url_prefix="/healthz")


# is the database connected?
database = False

# the list of quotes
QUOTES = default_quotes


@app.route("/add-quote", methods=["POST"])
def add_quote():
    """add quote to list of quotes"""
    if request.method == "POST":
        request_json = request.get_json()
        print(request_json, flush=True)

        if "quote" in request_json:
            QUOTES.append(request_json["quote"])
        else:
            # TODO propper logging
            print("Error: could not find 'quote' in request", flush=True)
            return "No 'quote' key in JSON", 500

        return "Quote received", 200
    return "Could not parse quote", 500


@app.route("/quotes")
def quotes():
    """return all quotes as JSON"""
    return jsonify(QUOTES)


@app.route("/quote")
def quote():
    """return single random quote"""
    return random.choice(QUOTES)
