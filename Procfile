web: python manage.py migrate --noinput && python manage.py create_admin && gunicorn bookshop.wsgi:application --bind 0.0.0.0:8000 --workers 1
