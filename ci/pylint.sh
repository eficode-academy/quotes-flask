#!/usr/bin/env bash

echo "Installing pylint with pip ..."

# install pylint
pip install --no-cache-dir --user pylint

# we run pylint with --exit-zero to always return code 0,
# so that the pipeline continues, even if the score is bad ...

echo "=================================================="
echo "Running pylint on frontend ..."
echo "=================================================="

pylint --exit-zero frontend/

echo "=================================================="
echo "Running pylint on backend ..."
echo "=================================================="

pylint --exit-zero backend/
