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
    echo "generating helm release for $VERSION"
	VERSION=$VERSION yq -i '.version = env(VERSION)' quotes-flask/Chart.yaml
    VERSION=$VERSION yq -i '.appVersion = env(VERSION)' quotes-flask/Chart.yaml
    VERSION=$VERSION yq -i '.backend.tag = env(VERSION)' quotes-flask/values.yaml
    VERSION=$VERSION yq -i '.frontend.tag = env(VERSION)' quotes-flask/values.yaml
    echo "helm push quotes-flask $VERSION"
    helm package quotes-flask
    helm push $QUOTES-$VERSION.tgz oci://ghcr.io/eficode-academy

done