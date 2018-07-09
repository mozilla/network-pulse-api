release: python manage.py migrate --no-input
web: python /app/generate_client_secrets.py && gunicorn pulseapi.wsgi
