"""Production settings with required secrets and PostgreSQL configuration."""

import os

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403
from .base import (
    database_from_environment,
    environment_boolean,
    environment_list,
    required_environment_variable,
)

if environment_boolean("DJANGO_DEBUG", default=False):
    raise ImproperlyConfigured("DJANGO_DEBUG cannot be enabled in production.")

DEBUG = False
SECRET_KEY = required_environment_variable("DJANGO_SECRET_KEY")
ALLOWED_HOSTS = environment_list("DJANGO_ALLOWED_HOSTS")
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "DJANGO_ALLOWED_HOSTS is required in production."
    )

database_engine = os.getenv("DATABASE_ENGINE", "postgresql").strip().lower()
if database_engine not in {"postgres", "postgresql"}:
    raise ImproperlyConfigured(
        "Production requires DATABASE_ENGINE=postgresql."
    )
DATABASES = {"default": database_from_environment(default_engine="postgresql")}

CSRF_TRUSTED_ORIGINS = environment_list("CSRF_TRUSTED_ORIGINS")
SECURE_CONTENT_TYPE_NOSNIFF = True

# Enable these only after the deployment serves HTTPS correctly.
HTTPS_ENABLED = environment_boolean("DJANGO_HTTPS_ENABLED", default=False)
SESSION_COOKIE_SECURE = HTTPS_ENABLED
CSRF_COOKIE_SECURE = HTTPS_ENABLED
SECURE_SSL_REDIRECT = HTTPS_ENABLED
SECURE_HSTS_SECONDS = 31536000 if HTTPS_ENABLED else 0

# Enable only when a trusted reverse proxy sets X-Forwarded-Proto.
if environment_boolean("DJANGO_TRUST_PROXY_HEADER", default=False):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
