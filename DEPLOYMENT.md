# ShellToolkit Deployment Guide

This project uses the final production architecture:

- **Web**: Django + Gunicorn + WhiteNoise
- **DB**: PostgreSQL
- **Container runtime**: Docker Compose

No in-stack Nginx container is required for this TFG deployment profile.
If you need external TLS termination, use your host/reverse proxy and forward to the web container.

## Why WhiteNoise (chosen architecture)

- Fewer moving parts than Nginx-based split for a TFG scope
- Static files are served directly by Django/Gunicorn with immutable hashed assets
- Easy local reproduction and reduced operational overhead

## 1) Prepare environment

Create `.env` from `.env.example` and set real production values.

Required variables:

- `SECRET_KEY`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `ADMIN_URL`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`

## 2) Build and run

```powershell
docker compose build

docker compose up -d
```

## 3) Verify health and static files

```powershell
curl http://127.0.0.1:8000/health/
```

Open `http://127.0.0.1:8000/` and verify CSS is loaded.

## 4) Admin and migrations

Migrations and collectstatic run automatically in `entrypoint.sh`.
To create an admin user:

```powershell
docker compose exec web python manage.py createsuperuser
```

Use custom admin path from `ADMIN_URL`.

## 5) Deploy security check

```powershell
docker compose exec web python manage.py check --deploy
```

If you run deploy checks outside Docker without PostgreSQL, use:

```powershell
$env:DJANGO_SETTINGS_MODULE = "config.settings.prod"
$env:USE_SQLITE_FOR_CHECK = "True"
.\.venv\Scripts\python.exe manage.py check --deploy
```

Keep `USE_SQLITE_FOR_CHECK=False` in real production.

