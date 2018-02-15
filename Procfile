release: python manage.py migrate
web: python /app/generate_client_secrets.py && gunicorn pulseapi.wsgi
