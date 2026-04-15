from urllib.parse import urlparse

from .base import *  # noqa: F401,F403

DEBUG = False
SECRET_KEY = config("SECRET_KEY")
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())


def _database_from_url(url):
    parsed = urlparse(url)
    if parsed.scheme not in {"postgres", "postgresql"}:
        raise ValueError("DATABASE_URL must use postgres:// or postgresql://")

    db_name = parsed.path.lstrip("/")
    if not db_name:
        raise ValueError("DATABASE_URL must include a database name")

    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": db_name,
        "USER": parsed.username or "",
        "PASSWORD": parsed.password or "",
        "HOST": parsed.hostname or "",
        "PORT": str(parsed.port or "5432"),
        "CONN_MAX_AGE": 60,
    }


USE_SQLITE_FOR_CHECK = config("USE_SQLITE_FOR_CHECK", default=False, cast=bool)

if USE_SQLITE_FOR_CHECK:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": _database_from_url(config("DATABASE_URL")),
    }

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Strict"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Strict"

SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 3600
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
