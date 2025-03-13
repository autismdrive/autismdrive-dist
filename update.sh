#!/usr/bin/env bash
###################################################################################################
# Run this script in the Production environment to update the backend after a code change.
###################################################################################################

APP_DIR=$(pwd)
cd ..
CONFIG_DIR=$(pwd)

# Activate the Python environment
source "${CONFIG_DIR}/python-env/bin/activate"

# Set the Flask app environment variable
FLASK_APP=${APP_DIR}/backend/app/__init__.py
export FLASK_APP

# Update the Python dependencies
cd "${APP_DIR}/backend" || return
pip install -r requirements.txt

# Update the database schema
flask db upgrade

# Refresh the Elasticsearch index
flask clearindex
flask initindex

