#!/usr/bin/env bash

# Ensure that google auth works (sigh)
python generate_client_secrets.py

# Make sure the Django database schemas are up to date
python manage.py migrate --no-input
