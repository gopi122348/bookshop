web: python manage.py migrate --noinput --run-syncdb; gunicorn bookshop.wsgi:application --bind 0.0.0.0:8000 --workers 1
