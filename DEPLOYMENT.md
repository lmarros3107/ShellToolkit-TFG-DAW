# Guia de despliegue de ShellToolkit

Este es el flujo de despliegue que estoy usando para el TFG.
Arquitectura en produccion:

- **Web**: Django + Gunicorn + WhiteNoise
- **DB**: PostgreSQL
- **Contenedores**: Docker Compose

En este proyecto no meto Nginx dentro del stack.
Si necesitas TLS, lo ideal es ponerlo fuera con un reverse proxy.

## Por que WhiteNoise

- Menos complejidad para un TFG
- Sirve estaticos con hash en produccion
- Facil de reproducir en local

## 1) Preparar entorno

Crea `.env` desde `.env.example` y asigna valores reales para produccion.

Variables obligatorias:

- `SECRET_KEY`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `ADMIN_URL`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`

## 2) Construir y levantar

### Linux (bash)

```bash
docker compose build
docker compose up -d
```

### Windows (PowerShell)

```powershell
docker compose build
docker compose up -d
```

## 3) Verificar salud y estaticos

### Linux (bash)

```bash
curl http://127.0.0.1:8000/health/
```

### Windows (PowerShell)

```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:8000/health/" -UseBasicParsing
```

Abre `http://127.0.0.1:8000/` y comprueba que carga bien el CSS.

Arquitectura de estaticos:

- `static/` es la carpeta fuente versionada en Git.
- `staticfiles/` se genera con `collectstatic` y no se versiona.

Para crear un usuario administrador:

```bash
docker compose exec web python manage.py createsuperuser
```

Recuerda usar la ruta de admin definida en `ADMIN_URL`.

## 4) Check de seguridad de despliegue

Dentro de Docker:

```bash
docker compose exec web python manage.py check --deploy
```

Fuera de Docker y sin PostgreSQL local:

### Linux (bash)

```bash
export DJANGO_SETTINGS_MODULE="config.settings.prod"
export USE_SQLITE_FOR_CHECK="True"
python manage.py check --deploy
```

### Windows (PowerShell)

```powershell
$env:DJANGO_SETTINGS_MODULE = "config.settings.prod"
$env:USE_SQLITE_FOR_CHECK = "True"
python manage.py check --deploy
```

En produccion real, deja `USE_SQLITE_FOR_CHECK=False`.

