#!/usr/bin/env bash

# We run hadolint with --no-fial to make it exit with code 0 and not stop the pipeline

echo "Running hadolint on the frontend Dockerfile ..."

docker run --rm -i hadolint/hadolint:latest hadolint --no-fail - <frontend/Dockerfile

echo "Running hadolint on the backend Dockerfile ..."

docker run --rm -i hadolint/hadolint:latest hadolint --no-fail - <backend/Dockerfile
