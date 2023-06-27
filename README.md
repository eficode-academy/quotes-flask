# quotes-flask

Small example flask application that displays quotes.

Developed to be used for training purposes, working with containerized / micro service applications.

## Application

The application consists of three components, frontend, backend and a database.

The frontend and backend are small python flask webservers that listen for HTTP requests.
For persistent storage, a postgresql database is used.

The base functionality of the application can be achieved by the frontend alone. The frontend listens for HTTP requests on port 5000 (the default for flask).

Adding the backend adds the functionality of submitting custom quotes, and retrieving them. Quotes are saved in memory, and will be lost on application restart.

Adding the database allows for persisting the custom quotes between application restarts.

The application images are stored in the GitHub container registry (ghcr.io), and can be found at `ghcr.io/eficode-academy/quotes-flask-frontend` and `ghcr.io/eficode-academy/quotes-flask-backend`, respectively.

Application images are built on pushes to the main branch using GitHub Actions.
"production" container images are available using the `release` tag from GitHub container registry.

## Deploying

### docker-compose

For a simple proof-of-concept, the included `docker-compose.yaml` can be used to deploy the application.

```sh
docker-compose up -d
```

The application will be available at `http://localhost:5000`

### Kubernetes

Kubernetes manifests are supplied in the `k8s/` directory.

For example, deploying the application using `kind`:

```sh
kind create cluster
kubectl apply -f k8s/
```

The manifests will create a NodePort service to access the frontend.

On linux you can simply connect to the `kind` container:

Use the following commands to get the IP address of the host:

```sh
kubectl get service
kubectl get nodes -o wide
```

For kind this will unintuitively be the `INTERNAL-IP`, for a cloud cluster use the `EXERNAL-IP`.

E.g. in a browser go to: `172.19.0.2:<nodePort>`

### Kubernetes using Helm

Helm chart is supplied in the `helm/quotes-flask` directory.

Deploying the application using `helm`:

```sh
helm install quotes-flask helm/quotes-flask
```

See the release with `helm list`, and get the NodePort with `kubectl get service frontend`.

You can change the values of the helm chart by supplying a `values.yaml` file, or by using the `--set` flag.

```sh
helm install quotes-flask helm/quotes-flask --set frontend.tag="3.0.0"
```

## Developing

### docker-compose

You can easily develop the application using the included docker-compose, which will bindmount the code for both the frontend and backend to allow you to edit the code and reload the flask webservers automatically.

```sh
docker-compose -f dev-docker-compose.yaml up -d
```

The application will be available at `http://localhost:5000`

You can use the `adminer` tool to check changes to the postgres database easily.

### In Kubernetes using Okteto

You can use `okteto` to achieve the same workflow, but running in kubernetes.

First install the okteto cli:

docs: https://www.okteto.com/docs/getting-started/

Generic Linux:

```sh
curl https://get.okteto.com -sSfL | sh
```

On Arch:

```sh
paru -S okteto
```

Then use the included `okteto.yml` to deploy the qutoes stack to a cluster, we will use kind.

```sh
kind create cluster
okteto deploy
```

Okteto will not create any outward facing service by default, so we can create a NodePort serivce, if we need it:

```sh
kubectl expose deployment frontend-okteto --port 5000 -type NodePort
```

For actually developing on the services we use the `okteto up <service>` command.

In one terminal type: `okteto up frontend`, and in a second terminal do `okteto up backend`.

Okteto will create a port forward to frontend, making it available at `http://localhost:5000`.
You can now make changes to the code, and these will be synchronized to the pod filesystems, and the flask webservers reloaded.

When you are done, use `okteto destroy` to take down the Okteto deployment.
Alternatively just delete the kind container.


## Versioning releases

By default, both Frontend and Backend will be build with the version "1.0.0", as defined in the Dockerfile.
You can override this by setting the `VERSION` environment variable when building the image.

```sh
docker build --build-arg VERSION=1.0.1 -t quotes-flask-frontend frontend
docker build --build-arg VERSION=1.0.1 -t quotes-flask-backend backend
```