release: python generate_client_secrets.py && python manage.py migrate --no-input
web: gunicorn pulseapi.wsgi
