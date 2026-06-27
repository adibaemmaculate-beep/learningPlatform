import os

from .base import *  # noqa: F401, F403

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # noqa: F405
    }
}

# Use real SMTP when credentials are configured; otherwise print to console.
if os.getenv('EMAIL_HOST_USER') and os.getenv('EMAIL_HOST_PASSWORD'):
    EMAIL_BACKEND = 'config.email_backend.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Allow .env to re-enable verification during local SMTP testing.
REQUIRE_EMAIL_VERIFICATION = os.getenv(
    'REQUIRE_EMAIL_VERIFICATION', 'False'
).lower() in ('true', '1', 'yes')
