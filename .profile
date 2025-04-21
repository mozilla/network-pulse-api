#!/bin/bash

# This script is only used by Heroku during dyno startup.
# It ensures setuptools is downgraded early to avoid install issues with legacy packages like django-allauth.
# Local environments ignore this file.

pip install "setuptools==65.5.1" --no-cache-dir --upgrade
