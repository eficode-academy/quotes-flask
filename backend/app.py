import json
from flask import Flask
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


@app.route("/add-quote")
def add_quote():
    pass


@app.route("/quotes")
def quotes():

    return json.dumps(default_quotes)
