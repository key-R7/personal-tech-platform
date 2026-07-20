"""Settings shared by development and production environments."""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def required_environment_variable(name):
    """Return a required environment variable or fail with a clear message."""
    value = os.getenv(name)
    if not value:
        raise ImproperlyConfigured(
            f"Missing required environment variable: {name}."
        )
    return value


def environment_boolean(name, default=False):
    """Read a boolean without treating every non-empty string as true."""
    value = os.getenv(name)
    if value is None:
        return default

    normalized_value = value.strip().lower()
    if normalized_value in {"1", "true", "yes", "on"}:
        return True
    if normalized_value in {"0", "false", "no", "off"}:
        return False
    raise ImproperlyConfigured(
        f"Environment variable {name} must be a boolean value."
    )


def environment_list(name, default=""):
    """Read a comma-separated environment variable as a clean list."""
    value = os.getenv(name, default)
    return [item.strip() for item in value.split(",") if item.strip()]


def environment_port(name, default=None):
    """Read and validate a TCP port from the environment."""
    value = os.getenv(name)
    if value is None or not value.strip():
        if default is None:
            raise ImproperlyConfigured(
                f"Missing required environment variable: {name}."
            )
        value = str(default)

    try:
        port = int(value)
    except ValueError as exc:
        raise ImproperlyConfigured(
            f"Environment variable {name} must be an integer port."
        ) from exc
    if not 1 <= port <= 65535:
        raise ImproperlyConfigured(
            f"Environment variable {name} must be between 1 and 65535."
        )
    return port


def database_from_environment(default_engine="sqlite"):
    """Build a SQLite or PostgreSQL Django database configuration."""
    engine = os.getenv("DATABASE_ENGINE", default_engine).strip().lower()

    if engine in {"sqlite", "sqlite3"}:
        database_name = os.getenv("DATABASE_NAME", "").strip()
        return {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": database_name or BASE_DIR / "db.sqlite3",
        }

    if engine in {"postgres", "postgresql"}:
        return {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": required_environment_variable("DATABASE_NAME"),
            "USER": required_environment_variable("DATABASE_USER"),
            "PASSWORD": required_environment_variable("DATABASE_PASSWORD"),
            "HOST": required_environment_variable("DATABASE_HOST"),
            "PORT": environment_port("DATABASE_PORT"),
        }

    raise ImproperlyConfigured(
        "DATABASE_ENGINE must be either 'sqlite' or 'postgresql'."
    )


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
    "blog",
    "projects",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.site_profile",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "core:home"
LOGOUT_REDIRECT_URL = "core:home"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "{levelname} {asctime} {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "blog": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
