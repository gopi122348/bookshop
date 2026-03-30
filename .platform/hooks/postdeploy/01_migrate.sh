#!/bin/bash
set -e
source /var/app/venv/*/bin/activate
cd /var/app/current

rm -f /var/app/current/db.sqlite3

python manage.py migrate --noinput

python manage.py shell -c "
from django.contrib.auth.models import User
u, created = User.objects.get_or_create(username='admin')
u.set_password('Admin1234')
u.is_superuser = True
u.is_staff = True
u.save()
print('Admin ready')
"