#!/usr/bin/env bash

REGISTRY="ghcr.io/eficode-academy"
FRONTEND_REPOSITORY="quotes-flask-frontend"
BACKEND_REPOSITORY="quotes-flask-backend"

GIT_TAG=$(git rev-parse HEAD)
TAG="release"

FRONTEND_IMAGE="$REGISTRY/$FRONTEND_REPOSITORY:$GIT_TAG"
BACKEND_IMAGE="$REGISTRY/$BACKEND_REPOSITORY:$GIT_TAG"

RELEASE_FRONTEND_IMAGE="$REGISTRY/$FRONTEND_REPOSITORY:$TAG"
RELEASE_BACKEND_IMAGE="$REGISTRY/$BACKEND_REPOSITORY:$TAG"

echo "Building images ..."

docker build -t "$FRONTEND_IMAGE" frontend
docker build -t "$BACKEND_IMAGE" backend

echo "Tagging images ..."

docker tag "$FRONTEND_IMAGE" "$RELEASE_FRONTEND_IMAGE"
docker tag "$BACKEND_IMAGE" "$RELEASE_BACKEND_IMAGE"

echo "Builiding versioned images ..."

VERSIONS="
1.0.0
2.0.0
3.0.0
4.0.0
5.0.0
"

# This should leverage the build chache to simply set different environment variable in each image

for VERSION in $VERSIONS; do
	FRONTEND_IMAGE="$REGISTRY/$FRONTEND_REPOSITORY:$VERSION"
	echo "Building image: $FRONTEND_IMAGE"
	docker build -t "$FRONTEND_IMAGE" "--build-arg=VERSION=$VERSION" frontend

	BACKEND_IMAGE="$REGISTRY/$BACKEND_REPOSITORY:$VERSION"
	echo "Building image: $BACKEND_IMAGE"
	docker build -t "$BACKEND_IMAGE" "--build-arg=VERSION=$VERSION" backend
done
