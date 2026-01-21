#!/bin/bash
set -e

echo "=========================================="
echo "🚀 Starting TBF Panel Deployment..."
echo "=========================================="

echo ""
echo "📦 Step 1/4: Running database migrations..."
python manage.py migrate --noinput
echo "✅ Migrations completed!"

echo ""
echo "👥 Step 2/4: Checking existing users..."
python manage.py shell << 'EOF'
from accounts.models import CustomUser
user_count = CustomUser.objects.count()
print(f"Current user count: {user_count}")
exit()
EOF

echo ""
echo "🔍 Step 3/4: Checking if users need to be created..."
python manage.py shell << 'EOF'
from accounts.models import CustomUser
import sys
user_count = CustomUser.objects.count()
if user_count == 0:
    print("⚠️  No users found in database!")
    print("📝 Creating all users now...")
    sys.exit(0)  # Exit code 0 = create users
else:
    print(f"✅ Users already exist ({user_count} users found)")
    sys.exit(1)  # Exit code 1 = skip creation
EOF

# Check exit code from previous command
if [ $? -eq 0 ]; then
    echo ""
    echo "⚙️  Step 4/4: Creating all users..."
    python manage.py create_all_users
    echo "✅ All users created successfully!"
else
    echo ""
    echo "⏭️  Step 4/4: Skipping user creation (users already exist)"
fi

echo ""
echo "=========================================="
echo "🌟 Starting Gunicorn server..."
echo "=========================================="
exec gunicorn tbf_panel.wsgi --bind 0.0.0.0:$PORT --log-file -