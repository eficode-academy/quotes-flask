#!/usr/bin/env bash

echo "Installing pylint with pip ..."

# install pylint
pip install --no-cache-dir --user pylint

# install project dependencies
pip install --no-cache-dir --user -r backend/requirements.txt
pip install --no-cache-dir --user -r frontend/requirements.txt

# we run pylint with --exit-zero to always return code 0,
# so that the pipeline continues, even if the score is bad ...

echo "=================================================="
echo "Running pylint on frontend ..."
echo "=================================================="

pylint --exit-zero --rcfile ./.pylintrc frontend/

echo "=================================================="
echo "Running pylint on backend ..."
echo "=================================================="

pylint --exit-zero --rcfile ./.pylintrc backend/
