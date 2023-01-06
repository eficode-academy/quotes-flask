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

echo "Pushing images ..."

docker push "$FRONTEND_IMAGE"
docker push "$BACKEND_IMAGE"
docker push "$RELEASE_FRONTEND_IMAGE"
docker push "$RELEASE_BACKEND_IMAGE"

echo "Pushing versioned images ..."

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
	echo "Pushing image: $FRONTEND_IMAGE"
	docker push "$FRONTEND_IMAGE"

	BACKEND_IMAGE="$REGISTRY/$BACKEND_REPOSITORY:$VERSION"
	echo "Pushing image: $BACKEND_IMAGE"
	docker push "$BACKEND_IMAGE"
done
