#!/bin/bash

set -e

# Check if pipenv is installed, if not, install it
echo "Installing pipenv..."
pip install pipenv

# Install dependencies
echo "Installing dependencies..."
pipenv install

# Activate virtual environment
echo "Activating virtual environment..."
pipenv shell

# Run migrations
echo "Running migrations..."
pipenv run python master_data/manage.py migrate
pipenv run python master_data/manage.py migrate master --database=master

# Collect static files
echo "Collecting static files..."
pipenv run python master_data/manage.py collectstatic

# Run Django server (this step might be omitted on production)
echo "Starting Django server..."
pipenv run python master_data/manage.py runserver
