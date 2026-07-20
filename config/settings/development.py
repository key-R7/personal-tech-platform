"""Local development settings; SQLite is used unless PostgreSQL is requested."""

import os

from .base import *  # noqa: F403
from .base import database_from_environment, environment_boolean, environment_list

# This fallback is intentionally limited to local development.
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-development-only-do-not-use-in-production",
)
DEBUG = environment_boolean("DJANGO_DEBUG", default=True)
ALLOWED_HOSTS = environment_list(
    "DJANGO_ALLOWED_HOSTS",
    default="localhost,127.0.0.1,[::1]",
)
DATABASES = {"default": database_from_environment(default_engine="sqlite")}
