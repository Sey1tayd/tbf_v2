#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Starting Gunicorn..."
exec gunicorn tbf_panel.wsgi --bind 0.0.0.0:$PORT --log-file -