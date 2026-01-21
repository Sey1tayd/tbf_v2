#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Checking if users exist..."
USER_COUNT=$(python manage.py shell -c "from accounts.models import CustomUser; print(CustomUser.objects.count())" 2>/dev/null || echo "0")

if [ "$USER_COUNT" -eq "0" ]; then
    echo "No users found. Creating all users..."
    python manage.py create_all_users
else
    echo "Users already exist ($USER_COUNT users). Skipping user creation."
fi

echo "Starting Gunicorn..."
exec gunicorn tbf_panel.wsgi --bind 0.0.0.0:$PORT --log-file -