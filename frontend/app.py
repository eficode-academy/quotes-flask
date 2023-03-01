"""
Frontend flask app, serves the graphical html version
and provides endpoints for getting/pushing quotes.
"""
import os
import random
import socket
import logging
import requests
import kubernetes
from kubernetes import client as kubernetes_client
from kubernetes import config as kubernetes_config
from flask import Flask, render_template, jsonify, request
from flask.wrappers import Response
from flask.logging import create_logger
from flask_healthz import healthz
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


# Read environment variables
BACKEND_HOST = os.environ.get("BACKEND_HOST", False)
BACKEND_PORT = os.environ.get("BACKEND_PORT", False)
# host for the backend, if not set default to False
BACKEND_ENDPOINT = bool(BACKEND_HOST and BACKEND_PORT)
# build the url for the backend
BACKEND_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}"
# whether the container is running in kubernetes, assumes that it is
ENABLE_KUBERNETS_FEATURES = bool(os.environ.get("NOT_RUNNING_IN_KUBERNETES", True))
# namespace pod is running in, must be set in the deployment, or loaded using downward api
NAMESPACE = os.environ.get("NAMESPACE", False)
# Version of the application
# TODO: add log warning about adding version
APPLICATION_VERSION = os.environ.get("APP_VERSION", "unknown")

if ENABLE_KUBERNETS_FEATURES:
    log.info("Running in Kubernetes mode.")
else:
    log.info("Not running in Kuberetes, disabling Kubernetes specific features.")

if NAMESPACE:
    log.info(
        "Found `namespace` environment variable with value `%s`, will use it to query pod names in the current namespace.",
        NAMESPACE,
    )
else:
    log.warning(
        "Namespace is not configured, set the environment variable `namespace` to the namespace the pod is deployed in to enable querying pod names."
    )


def check_backend_endpoint_env_var() -> bool:
    """Checks if the user has set the backend host environment variable"""
    if BACKEND_ENDPOINT:
        log.info(
            "Found 'backend_host' environment variable, will attempt to connect to the backend on: `%s`", BACKEND_URL
        )
        return True
    log.warning("'backend_host' environment variable not set, set this to connect to the backend.")
    return False


def check_if_database_is_available() -> bool:
    """Check if the database is reachable and should be used"""
    # check if the env var has been set
    if check_backend_endpoint_env_var():
        # try querying the backend
        try:
            backend_health_endpoint = f"{BACKEND_URL}/check-db-connection"
            response = requests.get(backend_health_endpoint, timeout=1)
            if response.status_code == 200:
                body = response.json()
                if "db-connected" in body:
                    if body["db-connected"] == "true":
                        return True
                    return False
            else:
                return False
            return False
        except (requests.ConnectionError, requests.ReadTimeout, KeyError):
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
            response = requests.get(backend_health_endpoint, timeout=1)
            return response.status_code == 200
        except requests.ConnectionError:
            return False
    else:
        return False


def get_random_quote_from_backend() -> str:
    """get a single quote from the backend"""
    response = requests.get(f"{BACKEND_URL}/quote", timeout=1)
    if response.status_code == 200:
        return response.text
    log.error("did not get a response 200 from backend")
    return ""


def get_all_quotes_from_backend() -> list[str]:
    """get list of all quotes form the backend"""
    response = requests.get(f"{BACKEND_URL}/quotes", timeout=1)
    if response.status_code == 200:
        return response.json()
    log.error("did not get a response 200 from backend")
    return []


@APP.route("/")
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

    frontend_hostname, backend_hostname, db_hostname = get_hostnames()
    # render the html template with arguments
    return render_template(
        "index.html",
        backend=backend_available,
        database=database_available,
        quotes=_quotes,
        frontend_hostname=frontend_hostname,
        backend_hostname=backend_hostname,
        db_hostname=db_hostname,
    )


@APP.route("/random-quote")
def random_quote():
    """return a random quote"""
    if check_if_backend_is_available():
        #  return random.choice(get_all_quotes_from_backend())
        return get_random_quote_from_backend()
    return random.choice(default_quotes)


@APP.route("/quotes")
def quotes():
    """Get all available quotes as JSON"""
    if check_if_backend_is_available():
        return jsonify(get_all_quotes_from_backend())
    return jsonify(default_quotes)


@APP.route("/add-quote", methods=["POST"])
def add_quote():
    """receive quote and pass it on to the backend"""
    log.info("attempting to add new quote to backend ...")
    if request.method == "POST":
        request_json = request.get_json()
        log.info("recieved JSON: %s", request_json)

        if "quote" in request_json:
            url = f"{BACKEND_URL}/add-quote"
            try:
                res = requests.post(url, json=request_json, timeout=1)
                if res.status_code == 200:
                    log.info("new quote successfully posted to backend.")
                    return "Quote received", 200
                log.error("could not successfully post new quote to backend.")
                return "error inserting quote", 500
            except (requests.ConnectionError, requests.ReadTimeout, KeyError) as err:
                log.error("encountered error when trying to pass quote to backend:")
                log.error(err)
                return "error inserting quote", 500
        else:
            log.error("could not find 'quote' in request")
            return "No 'quote' key in JSON", 500
    return "Could not parse quote", 500


def get_hostnames() -> tuple[str, str, str]:
    """returns tuple of (frontend_hostname, backend_hostname)"""
    log.info("Attempting to get backend hostname ...")
    frontend_hostname = socket.gethostname()
    if check_if_backend_is_available():
        try:
            response = requests.get(f"{BACKEND_URL}/hostname", timeout=1)
            if response.status_code == 200:
                resp_json = response.json()
                log.debug(resp_json)
                # if both backend and database are connected
                if "backend" in resp_json and "postgres" in resp_json:
                    backend_hostname = resp_json["backend"]
                    db_hostname = resp_json["postgres"]
                    return (frontend_hostname, backend_hostname, db_hostname)
                # if only backend is connected
                if "backend" in resp_json:
                    backend_hostname = resp_json["backend"]
                    return (frontend_hostname, backend_hostname, None)
        except (requests.ConnectionError, requests.ReadTimeout, KeyError) as err:
            log.error("Encountered an error trying to get hostname from backend: ")
            log.error(err)
            return (frontend_hostname, None)
    log.error("did not get a response 200 from backend")
    return (frontend_hostname, None, None)


@APP.route("/hostname")
def hostname():
    """return the hostname of the given container"""
    frontend_hostname, backend_hostname, db_hostname = get_hostnames()
    hostnames = {"frontend": frontend_hostname, "backend": backend_hostname, "postgres": db_hostname}
    return jsonify(hostnames)


@APP.route("/pod-names")
def get_pod_names() -> Response:
    """
    Query kubernetes API to get hostnames of all frontend, backend and postgres pods.
    Returns JSON dict of pod names.
    """

    # only try to contact the kubernetes api server, if actually running in kubernetes
    if not ENABLE_KUBERNETS_FEATURES:
        return jsonify({"message": "Not currently running in Kubernetes, cannot get pod names."})
    if not NAMESPACE:
        return jsonify(
            {
                "message": "`NAMESPACE` environment variable not set, specify to enable querying the Kubernetes API for pod names."
            }
        )

    # get config for querying the k8s api from the namespace and the service account
    kubernetes_config.load_incluster_config()
    # create a client for the k8s api
    k8s_client = kubernetes_client.CoreV1Api()
    # query the API for all of the pods in the current namespace
    response = None
    try:
        response = k8s_client.list_namespaced_pod(namespace=NAMESPACE)
    except kubernetes.client.exceptions.ApiException:
        log.error("Caugth an API error when trying to query the Kubernetes API to get pod info.")
        log.error("You are most likely missing a service account with read access for pods in this namespace.")
        return jsonify(
            {
                "message": "Got an API error when trying to get pod names from the k8s API, "
                "you are likely missing a ServiceAccount with proper permissions, see the readme for quotes-flask."
            }
        )

    # hold a list of pods for each application
    frontend_pods = []
    backend_pods = []
    postgres_pods = []
    # iterate over the returned pods
    # TODO: this coud probably be done more elegantly
    for pod in response.items:
        pod_name = pod.metadata.name
        if "frontend" in pod_name:
            frontend_pods.append(pod_name)
        elif "backend" in pod_name:
            backend_pods.append(pod_name)
        elif "postgres" in pod_name:
            postgres_pods.append(pod_name)
        else:
            log.info(
                str.format(
                    "Pod Name: `% s` dit not match any of the substrings `frontend`, `backend` or `postgres`.",
                    pod_name,
                )
            )

    pod_names = {"frontend_pods": frontend_pods, "backend_pods": backend_pods, "postgres_pods": postgres_pods}

    return jsonify(pod_names)


@APP.route("/version")
def version():
    """return the version of the frontend"""
    return jsonify({"version": APPLICATION_VERSION})


@APP.route("/backend/version")
def backend_version():
    """return the version of the backend"""
    response = requests.get(f"{BACKEND_URL}/version", timeout=1)
    if response.status_code == 200:
        return response.text
    log.error("did not get a response 200 from backend")
    return jsonify({"version": "error getting version"})


@APP.route("/database/version")
def database_version():
    """return the version of the backend"""
    response = requests.get(f"{BACKEND_URL}/database/version", timeout=1)
    if response.status_code == 200:
        return response.text
    log.error("did not get a response 200 from backend %s", response.text)

    return jsonify({"version": "error getting version"})


@APP.route("/ip")
def return_ip():
    """return the ip address of the host"""
    ip = socket.gethostbyname(socket.gethostname())
    return ip
