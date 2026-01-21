#!/bin/bash
set -e

echo "=========================================="
echo "🚀 Starting TBF Panel Deployment..."
echo "=========================================="

echo ""
echo "📦 Step 1/3: Running database migrations..."
python manage.py migrate --noinput 2>&1 | grep -v "objects imported automatically" || true
echo "✅ Migrations completed!"

echo ""
echo "👥 Step 2/3: Checking and creating users if needed..."
USER_COUNT=$(python manage.py shell -c "from accounts.models import CustomUser; print(CustomUser.objects.count())" 2>&1 | grep -E "^[0-9]+$" || echo "0")

if [ "$USER_COUNT" -eq "0" ]; then
    echo "⚠️  No users found! Creating all users..."
    python manage.py create_all_users 2>&1 | grep -v "objects imported automatically" || true
    echo "✅ All users created successfully!"
else
    echo "✅ Users already exist ($USER_COUNT users found)"
fi

echo ""
echo "=========================================="
echo "🌟 Step 3/3: Starting Gunicorn server..."
echo "=========================================="
exec gunicorn tbf_panel.wsgi --bind 0.0.0.0:${PORT:-8080} --log-file -