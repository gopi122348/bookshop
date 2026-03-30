#!/bin/bash

cd /var/app/current

/var/app/venv/staging-LQM1lest/bin/python manage.py migrate --noinput
