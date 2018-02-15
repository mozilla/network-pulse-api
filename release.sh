#!/usr/bin/env bash

# Make Django migrations, just in case...
python manage.py makemigrations

# Then migrate up.
python manage.py migrate
