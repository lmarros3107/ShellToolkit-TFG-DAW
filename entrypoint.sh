#!/bin/sh
set -e

python -c "import os; print('Using settings:', os.environ.get('DJANGO_SETTINGS_MODULE', 'config.settings.dev'))"

if [ "${USE_SQLITE_FOR_CHECK:-False}" != "True" ]; then
  python - <<'PY'
import os
import time
from urllib.parse import urlparse

import psycopg

url = os.environ.get("DATABASE_URL", "")
if not url:
    raise SystemExit("DATABASE_URL is required when USE_SQLITE_FOR_CHECK is not True")

parsed = urlparse(url)
conninfo = {
    "host": parsed.hostname or "db",
    "port": parsed.port or 5432,
    "user": parsed.username or "postgres",
    "password": parsed.password or "",
    "dbname": parsed.path.lstrip("/") or "postgres",
}

for attempt in range(1, 31):
    try:
        with psycopg.connect(**conninfo):
            print("Database is ready")
            break
    except Exception as exc:
        print(f"Waiting for database ({attempt}/30): {exc}")
        time.sleep(2)
else:
    raise SystemExit("Database did not become ready in time")
PY
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"

