#!/bin/sh
set -e

: "${DJANGO_SETTINGS_MODULE:=config.settings.prod}"
export DJANGO_SETTINGS_MODULE

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"
