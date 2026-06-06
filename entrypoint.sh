#!/usr/bin/env sh
set -eu

mkdir -p /app/data /app/media/audio /app/staticfiles

python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py seed_demo

exec "$@"
