"""
Backend flask app, provides an API for retrieving and
storing quotes, can connect to an external database
to persist quotes.
"""
import random
import os
import socket
import logging
from flask import Flask, jsonify, request
from flask_healthz import healthz
import db
from quotes import default_quotes

# configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s")

# create the flask app
app = Flask(__name__)


# add flask-healthz config to flask config
app.config["HEALTHZ"] = {"live": "healthz.liveness", "ready": "healthz.readiness"}
# create the healthz endpoints
app.register_blueprint(healthz, url_prefix="/healthz")

# pass app object to db class
db.import_app(app)


# host for the backend, if not set default to False
DATABASE_HOST = os.environ.get("db_host", False)
DATABASE_PORT = os.environ.get("db_port", False)
DATABASE_USER = os.environ.get("db_user", False)
DATABASE_PASSWORD = os.environ.get("db_password", False)
DATABASE_NAME = os.environ.get("db_name", False)

DB_CONN = {
    "host": DATABASE_HOST,
    "port": DATABASE_PORT,
    "user": DATABASE_USER,
    "password": DATABASE_PASSWORD,
    "name": DATABASE_NAME,
}

# the list of quotes
QUOTES = default_quotes


def check_db_creds_are_set() -> bool:
    """Checks if the user has set all env vars needed for connecting to the db, and warns them otherwise"""
    all_set = True
    if not DATABASE_HOST:
        app.logger.warning("'db_host' environment variable not set, set this to connect to the database.")
        all_set = False

    if not DATABASE_USER:
        app.logger.warning("'db_user' environment variable not set, set this to connect to the database.")
        all_set = False

    if not DATABASE_PASSWORD:
        app.logger.warning("'db_password' environment variable not set, set this to connect to the database.")
        all_set = False

    if not DATABASE_NAME:
        app.logger.warning("'db_name' environment variable not set, set this to connect to the database.")
        all_set = False

    return all_set


def check_if_db_is_available() -> bool:
    """Check if the db is reachable and should be used"""
    app.logger.info("Checking connection to the database ...")
    if check_db_creds_are_set():
        return db.check_connection(DB_CONN)
    app.logger.warning("database connection environment variables not set, cannot test connection.")
    return False


@app.route("/check-db-connection")
def check_db_connection():
    """Other services can ask if the db is connected."""
    if check_if_db_is_available():
        return jsonify({"db-connected": "true"})
    return jsonify({"db-connected": "false"})


@app.route("/add-quote", methods=["POST"])
def add_quote():
    """add quote to list of quotes"""
    if request.method == "POST":
        request_json = request.get_json()

        if "quote" in request_json:
            quote_to_insert = request_json["quote"]
            QUOTES.append(quote_to_insert)

            if check_if_db_is_available():
                inserted = db.insert_quote(quote_to_insert, DB_CONN)
                if inserted:
                    app.logger.info(f"Successfully inserted '{quote}' into db.")
                else:
                    app.logger.error(f"could insert '{quote}' into db.")
        else:
            app.logger.error("could not find 'quote' in request")
            return "No 'quote' key in JSON", 500

        return "Quote received", 200
    return "Could not parse quote", 500


@app.route("/quotes")
def quotes():
    """return all quotes as JSON"""
    if check_if_db_is_available():
        all_quotes = db.get_quotes(DB_CONN)
        if all_quotes:
            return jsonify(all_quotes)
        return jsonify([])
    return jsonify(QUOTES)


@app.route("/quote")
def quote():
    """return single random quote"""
    if check_if_db_is_available():
        all_quotes = db.get_quotes(DB_CONN)
        if all_quotes:
            return random.choice(all_quotes)
        app.logger.error("Could not get quotes from the database.")
        return ""
    # if db not available, use in-memory quotes
    return random.choice(QUOTES)


@app.route("/hostname")
def hostname():
    """return the hostname of the given container"""
    return jsonify({"backend": socket.gethostname()})
