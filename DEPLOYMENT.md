# Guia de despliegue de ShellToolkit

Este proyecto usa la siguiente arquitectura de produccion:

- **Web**: Django + Gunicorn + WhiteNoise
- **DB**: PostgreSQL
- **Runtime de contenedores**: Docker Compose

Para el alcance de este TFG no se incluye un contenedor Nginx dentro del stack.
Si necesitas TLS externo, usa tu reverse proxy y reenvia al contenedor web.

## Por que WhiteNoise

- Menos piezas operativas que una separacion Django + Nginx
- Estaticos servidos por Django/Gunicorn con assets hasheados
- Flujo facil de reproducir en local

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

Abre `http://127.0.0.1:8000/` y verifica que el CSS carga correctamente.

Arquitectura de estaticos:

- `static/` es el directorio fuente versionado en Git.
- `staticfiles/` es salida generada por `collectstatic` al arrancar el contenedor y no debe versionarse.

Para crear un usuario administrador:

```bash
docker compose exec web python manage.py createsuperuser
```

Usa la ruta de admin definida en `ADMIN_URL`.

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

En produccion real, mantén `USE_SQLITE_FOR_CHECK=False`.

