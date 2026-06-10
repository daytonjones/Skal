#!/usr/bin/env bash
set -e

echo "⏳ Waiting for Postgres to be ready…"
until pg_isready -h skal_db -U "$POSTGRES_USER" -d "$POSTGRES_DB" >/dev/null 2>&1; do
  sleep 2
done
echo "✅ Postgres is up—migrating database."

# 1) Collect static files so CSS/JS changes are always served fresh
python manage.py collectstatic --noinput

# 2) Run all migrations
python manage.py migrate --noinput

# 2) Conditionally create superuser
#    Only if the three env‐vars are provided
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  echo "🛡️  Ensuring superuser '$DJANGO_SUPERUSER_USERNAME' exists…"
  python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='${DJANGO_SUPERUSER_USERNAME}').exists():
    User.objects.create_superuser(
        '${DJANGO_SUPERUSER_USERNAME}',
        '${DJANGO_SUPERUSER_EMAIL}',
        '${DJANGO_SUPERUSER_PASSWORD}'
    )
EOF
else
  echo "⚠️  DJANGO_SUPERUSER_{USERNAME,EMAIL,PASSWORD} not fully set — skipping superuser creation."
fi

# Ensure media upload directory exists and is writable
mkdir -p /app/media
chmod 755 /app/media

service cron start

echo "🚀 Launching application…"
exec "$@"

