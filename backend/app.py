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
from flask.logging import create_logger
from flask_healthz import healthz
import db
from quotes import default_quotes

# configure logging
logging.basicConfig(level=logging.INFO)

# create the flask app
APP = Flask(__name__)
log = create_logger(APP)


# add flask-healthz config to flask config
APP.config["HEALTHZ"] = {"live": "healthz.liveness", "ready": "healthz.readiness"}
# create the healthz endpoints
APP.register_blueprint(healthz, url_prefix="/healthz")

# pass app object to db class
db.import_app(APP)


# host for the backend, if not set default to False
DATABASE_HOST = os.environ.get("DB_HOST", False)
DATABASE_PORT = os.environ.get("DB_PORT", False)
DATABASE_USER = os.environ.get("DB_USER", False)
DATABASE_PASSWORD = os.environ.get("DB_PASSWORD", False)
DATABASE_NAME = os.environ.get("DB_NAME", False)

# Create libpq connection string
DB_CONN = f"host={DATABASE_HOST} port={DATABASE_PORT} dbname={DATABASE_NAME} user={DATABASE_USER} password={DATABASE_PASSWORD}"

# the list of quotes
QUOTES = default_quotes


def check_db_creds_are_set() -> bool:
    """Checks if the user has set all env vars needed for connecting to the db, and warns them otherwise"""
    all_set = True
    if not DATABASE_HOST:
        log.warning("'DB_HOST' environment variable not set, set this to connect to the database.")
        all_set = False

    if not DATABASE_USER:
        log.warning("'DB_USER' environment variable not set, set this to connect to the database.")
        all_set = False

    if not DATABASE_PASSWORD:
        log.warning("'DB_PASSWORD' environment variable not set, set this to connect to the database.")
        all_set = False

    if not DATABASE_NAME:
        log.warning("'DB_NAMES' environment variable not set, set this to connect to the database.")
        all_set = False

    return all_set


def check_if_db_is_available() -> bool:
    """Check if the db is reachable and should be used"""
    log.info("Checking connection to the database ...")
    if check_db_creds_are_set():
        return db.check_connection(DB_CONN)
    log.warning("database connection environment variables not set, cannot test connection.")
    return False


@APP.route("/check-db-connection")
def check_db_connection():
    """Other services can ask if the db is connected."""
    if check_if_db_is_available():
        return jsonify({"db-connected": "true"})
    return jsonify({"db-connected": "false"})


@APP.route("/add-quote", methods=["POST"])
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
                    log.info("Successfully inserted '%s' into db.", quote_to_insert)
                else:
                    log.error("could insert '%s' into db.", quote_to_insert)
        else:
            log.error("could not find 'quote' in request")
            return "No 'quote' key in JSON", 500

        return "Quote received", 200
    return "Could not parse quote", 500


@APP.route("/")
def index():
    """default route"""
    return "Hello from the backend!"


@APP.route("/quotes")
def quotes():
    """return all quotes as JSON"""
    if check_if_db_is_available():
        all_quotes = db.get_quotes(DB_CONN)
        if all_quotes:
            return jsonify(all_quotes)
        return jsonify([])
    return jsonify(QUOTES)


@APP.route("/quote")
def quote():
    """return single random quote"""
    if check_if_db_is_available():
        all_quotes = db.get_quotes(DB_CONN)
        if all_quotes:
            return random.choice(all_quotes)
        log.error("Could not get quotes from the database.")
        return ""
    # if db not available, use in-memory quotes
    return random.choice(QUOTES)


@APP.route("/hostname")
def hostname():
    """return the hostname of the given container"""
    backend_hostname = socket.gethostname()
    if check_if_db_is_available():
        db_hostname = db.get_db_hostname(DB_CONN)
        return jsonify({"backend": backend_hostname, "postgres": db_hostname})
    return jsonify({"backend": backend_hostname, "postgres": None})


@APP.route("/version")
def version():
    """return the version of the given container"""
    return jsonify({"version": os.environ.get("APP_VERSION", "unknown")})


@APP.route("/database/version")
def db_version():
    """return the version of the database"""
    if check_if_db_is_available():
        log.info("Getting database version ...")
        return jsonify({"version": db.get_version(DB_CONN)})
    return jsonify({"version": "unknown"})
