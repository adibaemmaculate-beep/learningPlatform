import os

from .base import *  # noqa: F401, F403

DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')

# Database: PostgreSQL when DB_ENGINE is set to "postgres"/"postgresql",
# otherwise fall back to SQLite (no extra DB server required).
if os.getenv('DB_ENGINE', 'sqlite').lower().startswith('postgres'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'learning_platform'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',  # noqa: F405
            # Wait (seconds) for a lock instead of failing under concurrent
            # writes from multiple Gunicorn workers.
            'OPTIONS': {'timeout': 20},
        }
    }

EMAIL_BACKEND = 'config.email_backend.EmailBackend'

# Static files: compress + hash with WhiteNoise (served by Gunicorn directly).
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# We sit behind a TLS-terminating proxy (Tailscale Funnel / Nginx), so trust
# the X-Forwarded-Proto header to detect HTTPS. Without this, SECURE_SSL_REDIRECT
# below causes an infinite redirect loop.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'True').lower() in ('true', '1', 'yes')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Django 4+ requires the public origin(s) to be trusted for POST/admin/login.
# Comma-separated, each MUST include the scheme, e.g.
# CSRF_TRUSTED_ORIGINS=https://my-machine.tail1234.ts.net
CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if o.strip()
]
