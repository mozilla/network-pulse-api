#!/usr/bin/env bash

# Ensure a client_secrets.json file for google authentication
python generate_client_secrets.py

# Make Django migrations, just in case...
python manage.py makemigrations

# Then migrate up.
python manage.py migrate

# Finally, start up the system
python manage.py runserver "0.0.0.0:$PORT"
