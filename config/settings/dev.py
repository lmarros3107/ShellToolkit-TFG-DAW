from .base import *  # noqa: F401,F403

DEBUG = True

# In development, serve static assets directly via Django staticfiles finders.
# This avoids stale STATIC_ROOT/WhiteNoise behavior while editing local assets.
MIDDLEWARE = [
    mw for mw in MIDDLEWARE if mw != "whitenoise.middleware.WhiteNoiseMiddleware"
]

STORAGES["staticfiles"] = {
    "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Relaxed CSP for local development tooling.
CSP_HEADER = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline'; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
    "font-src 'self' https://fonts.gstatic.com; "
    "img-src 'self' data:; "
    "connect-src 'self'; "
    "frame-ancestors 'none'; "
    "base-uri 'self'; "
    "object-src 'none'; "
    "form-action 'self';"
)
