web: rm -f /var/app/current/db.sqlite3 /var/app/staging/db.sqlite3 && python manage.py migrate --noinput && gunicorn bookshop.wsgi:application --bind 0.0.0.0:8000
