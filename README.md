# ShellToolkit

ShellToolkit is a public educational Django platform for pentesting-lab support.
The application generates command text and playbooks only, and never executes commands on the server.

## Stack

- Django 4.2
- WhiteNoise for static files in production
- Gunicorn for WSGI serving
- PostgreSQL for production database
- Docker Compose for deployment

## Local development

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py loaddata shells/fixtures/initial_shells.json
.\.venv\Scripts\python.exe manage.py loaddata listeners/fixtures/initial_listeners.json
.\.venv\Scripts\python.exe manage.py loaddata playbooks/fixtures/linux_playbooks.json
.\.venv\Scripts\python.exe manage.py loaddata playbooks/fixtures/windows_playbooks.json
.\.venv\Scripts\python.exe manage.py runserver
```

## Static files notes

- `base.html` uses `{% load static %}` and valid `{% static '...' %}` paths.
- `config/settings/base.py` defines `STATIC_URL`, `STATICFILES_DIRS`, `STATIC_ROOT`.
- Development uses plain static storage.
- Production uses WhiteNoise compressed manifest storage.

## Production deployment

Use Docker Compose (web + db):

```powershell
docker compose build
docker compose up -d
```

Detailed production steps are in `DEPLOYMENT.md`.

## Security checks

Run deploy check inside container:

```powershell
docker compose exec web python manage.py check --deploy
```

Local fallback for deploy check when PostgreSQL is unavailable:

```powershell
$env:DJANGO_SETTINGS_MODULE = "config.settings.prod"
$env:USE_SQLITE_FOR_CHECK = "True"
.\.venv\Scripts\python.exe manage.py check --deploy
```
