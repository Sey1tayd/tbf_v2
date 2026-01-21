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
echo "👥 Step 2/4: Checking and creating users if needed..."
USER_COUNT=$(python manage.py shell -c "from accounts.models import CustomUser; print(CustomUser.objects.count())" 2>&1 | grep -E "^[0-9]+$" || echo "0")
EXPECTED_USERS=101  # 100 normal user + 1 admin

if [ "$USER_COUNT" -lt "$EXPECTED_USERS" ]; then
    if [ "$USER_COUNT" -eq "0" ]; then
        echo "⚠️  No users found! Creating all users..."
    else
        echo "⚠️  Only $USER_COUNT users found. Creating missing users (target: $EXPECTED_USERS)..."
    fi
    python manage.py create_all_users 2>&1 | grep -v "objects imported automatically" || true
    FINAL_COUNT=$(python manage.py shell -c "from accounts.models import CustomUser; print(CustomUser.objects.count())" 2>&1 | grep -E "^[0-9]+$" || echo "0")
    echo "✅ User creation completed! Total users: $FINAL_COUNT"
else
    echo "✅ All users already exist ($USER_COUNT users found)"
fi

echo ""
echo "📚 Step 3/4: Loading questions from questions.json..."
python manage.py load_questions 2>&1 | grep -v "objects imported automatically" || true
echo "✅ Questions loaded!"

echo ""
echo "=========================================="
echo "🌟 Step 4/4: Starting Gunicorn server..."
echo "=========================================="
exec gunicorn tbf_panel.wsgi --bind 0.0.0.0:${PORT:-8080} --log-file -