# ShellToolkit

ShellToolkit es mi proyecto de TFG (DAW) hecho con Django para apoyar practicas de pentesting en laboratorio.
La app solo genera texto (comandos y playbooks) y no ejecuta nada en el servidor.

## Stack

- Django 4.2
- WhiteNoise para estaticos en produccion
- Gunicorn como servidor WSGI
- PostgreSQL para base de datos en produccion
- Docker Compose para despliegue

## Desarrollo local

### Linux (bash)

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

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py loaddata shells/fixtures/initial_shells.json
python manage.py loaddata listeners/fixtures/initial_listeners.json
python manage.py loaddata playbooks/fixtures/linux_playbooks.json
python manage.py loaddata playbooks/fixtures/windows_playbooks.json
python manage.py runserver
```

## Notas de archivos estaticos

- `base.html` usa `{% load static %}` y rutas `{% static '...' %}` validas.
- `config/settings/base.py` define `STATIC_URL`, `STATICFILES_DIRS`, `STATIC_ROOT`, `MEDIA_URL` y `MEDIA_ROOT`.
- `static/` es la carpeta fuente de estilos, JS e imagenes.
- `staticfiles/` es una salida generada por `collectstatic` (no se versiona).
- En desarrollo se usa `config.settings.dev` y en produccion `config.settings.prod`.
- `config/static_storage.py` se mantiene para asegurar URLs correctas con `/static/...`.

## Seleccion de settings

- CLI (`manage.py`) usa por defecto `config.settings.dev`.
- WSGI/ASGI usan por defecto `config.settings.prod`.
- Si hace falta, define `DJANGO_SETTINGS_MODULE` de forma explicita.

## Despliegue en produccion

Usa Docker Compose (web + db):

```bash
docker compose build
docker compose up -d
```

Para el detalle completo, revisa `DEPLOYMENT.md`.

## Comprobaciones de seguridad

Dentro del contenedor:

```bash
docker compose exec web python manage.py check --deploy
```

Fallback local sin PostgreSQL:

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

