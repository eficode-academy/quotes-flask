#!/usr/bin/env bash

REGISTRY="ghcr.io/eficode-academy"
FRONTEND_REPOSITORY="quotes-flask-frontend"
BACKEND_REPOSITORY="quotes-flask-backend"
HELM_REPOSITORY="quotes-flask-helm"
QUOTES="quotes-flask"
VERSIONS="
1.0.0
2.0.0
3.0.0
4.0.0
5.0.0
"

echo "Creating Helm releases ..."
cd helm

for VERSION in $VERSIONS; do
    echo "Creating Helm release: $VERSION"
    FRONTEND_IMAGE="$REGISTRY/$FRONTEND_REPOSITORY:$VERSION"
    BACKEND_IMAGE="$REGISTRY/$BACKEND_REPOSITORY:$VERSION"
    echo "generating helm release for $VERSION"
	VERSION=$VERSION yq -i '.version = env(VERSION)' quotes-flask/Chart.yaml
    VERSION=$VERSION yq -i '.appVersion = env(VERSION)' quotes-flask/Chart.yaml
    FRONTEND_IMAGE=$FRONTEND_IMAGE yq -i '.spec.template.spec.containers[0].image = env(FRONTEND_IMAGE)' quotes-flask/templates/frontend-deployment.yaml
    BACKEND_IMAGE=$BACKEND_IMAGE yq -i '.spec.template.spec.containers[0].image = env(BACKEND_IMAGE)' quotes-flask/templates/backend-deployment.yaml
    echo "helm push quotes-flask $VERSION"
    helm package quotes-flask
    echo "$PWD"
    helm push $QUOTES-$VERSION.tgz oci://ghcr.io/eficode-academy

done