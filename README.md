# ShellToolkit

ShellToolkit is a public educational Django platform for pentesting-lab support.
The application generates command text and playbooks only, and never executes commands on the server.

## Stack

- Django 4.2
- WhiteNoise for static files in production
- Gunicorn for WSGI serving
- PostgreSQL for production database
- Docker Compose for deployment

## Local development (Linux)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py loaddata shells/fixtures/initial_shells.json
python manage.py loaddata listeners/fixtures/initial_listeners.json
python manage.py loaddata playbooks/fixtures/linux_playbooks.json
python manage.py loaddata playbooks/fixtures/windows_playbooks.json
python manage.py runserver
```

## Static files notes

- `base.html` uses `{% load static %}` and valid `{% static '...' %}` paths.
- `config/settings/base.py` defines `STATIC_URL`, `STATICFILES_DIRS`, `STATIC_ROOT`.
- Development uses plain static storage.
- Production uses WhiteNoise compressed manifest storage.

## Production deployment

Use Docker Compose (web + db):

```bash
docker compose build
docker compose up -d
```

Detailed production steps are in `DEPLOYMENT.md`.

## Security checks

Run deploy check inside container:

```bash
docker compose exec web python manage.py check --deploy
```

Local fallback for deploy check when PostgreSQL is unavailable:

```bash
export DJANGO_SETTINGS_MODULE="config.settings.prod"
export USE_SQLITE_FOR_CHECK="True"
python manage.py check --deploy
```
