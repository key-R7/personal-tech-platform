import json
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from config.settings.base import (
    database_from_environment,
    environment_boolean,
    environment_list,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIGURATION_VARIABLES = (
    "DJANGO_SECRET_KEY",
    "DJANGO_DEBUG",
    "DJANGO_ALLOWED_HOSTS",
    "DATABASE_ENGINE",
    "DATABASE_NAME",
    "DATABASE_USER",
    "DATABASE_PASSWORD",
    "DATABASE_HOST",
    "DATABASE_PORT",
)


def settings_subprocess(module, extra_environment=None):
    """Load a settings module in an isolated child process."""
    environment = os.environ.copy()
    for variable in CONFIGURATION_VARIABLES:
        environment.pop(variable, None)
    environment.update(extra_environment or {})
    command = (
        "import json; "
        f"from {module} import ALLOWED_HOSTS, DATABASES, DEBUG; "
        "print(json.dumps({"
        "'debug': DEBUG, "
        "'allowed_hosts': ALLOWED_HOSTS, "
        "'database': DATABASES['default']"
        "}, default=str))"
    )
    return subprocess.run(
        [sys.executable, "-c", command],
        cwd=PROJECT_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )


class EnvironmentSettingTests(SimpleTestCase):
    def test_boolean_environment_values_are_parsed_explicitly(self):
        for value in ("1", "true", "YES", "on"):
            with self.subTest(value=value), patch.dict(
                os.environ, {"TEST_BOOLEAN": value}
            ):
                self.assertTrue(environment_boolean("TEST_BOOLEAN"))

        for value in ("0", "false", "NO", "off"):
            with self.subTest(value=value), patch.dict(
                os.environ, {"TEST_BOOLEAN": value}
            ):
                self.assertFalse(environment_boolean("TEST_BOOLEAN"))

    def test_invalid_boolean_environment_value_fails_clearly(self):
        with patch.dict(os.environ, {"TEST_BOOLEAN": "sometimes"}):
            with self.assertRaises(ImproperlyConfigured):
                environment_boolean("TEST_BOOLEAN")

    def test_comma_separated_environment_values_are_cleaned(self):
        with patch.dict(
            os.environ,
            {"TEST_LIST": "localhost, 127.0.0.1, ,example.com"},
        ):
            self.assertEqual(
                environment_list("TEST_LIST"),
                ["localhost", "127.0.0.1", "example.com"],
            )

    def test_postgresql_configuration_uses_environment_fields(self):
        database_environment = {
            "DATABASE_ENGINE": "postgresql",
            "DATABASE_NAME": "portfolio",
            "DATABASE_USER": "portfolio_user",
            "DATABASE_PASSWORD": "temporary-test-password",
            "DATABASE_HOST": "database.example.test",
            "DATABASE_PORT": "5433",
        }
        with patch.dict(os.environ, database_environment):
            configuration = database_from_environment()

        self.assertEqual(configuration["ENGINE"], "django.db.backends.postgresql")
        self.assertEqual(configuration["NAME"], "portfolio")
        self.assertEqual(configuration["USER"], "portfolio_user")
        self.assertEqual(configuration["PASSWORD"], "temporary-test-password")
        self.assertEqual(configuration["HOST"], "database.example.test")
        self.assertEqual(configuration["PORT"], 5433)


class SettingsModuleTests(SimpleTestCase):
    def test_default_development_settings_load_with_sqlite(self):
        result = settings_subprocess("config.settings.development")

        self.assertEqual(result.returncode, 0, result.stderr)
        configuration = json.loads(result.stdout)
        self.assertTrue(configuration["debug"])
        self.assertEqual(
            configuration["database"]["ENGINE"],
            "django.db.backends.sqlite3",
        )
        self.assertIn("127.0.0.1", configuration["allowed_hosts"])

    def test_production_settings_require_secret_key(self):
        result = settings_subprocess("config.settings.production")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DJANGO_SECRET_KEY", result.stderr)

    def test_production_settings_force_debug_off_and_postgresql(self):
        result = settings_subprocess(
            "config.settings.production",
            {
                "DJANGO_SECRET_KEY": "temporary-production-test-secret",
                "DJANGO_ALLOWED_HOSTS": "portfolio.example.com",
                "DATABASE_ENGINE": "postgresql",
                "DATABASE_NAME": "portfolio",
                "DATABASE_USER": "portfolio_user",
                "DATABASE_PASSWORD": "temporary-test-password",
                "DATABASE_HOST": "database.example.test",
                "DATABASE_PORT": "5432",
            },
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        configuration = json.loads(result.stdout)
        self.assertFalse(configuration["debug"])
        self.assertEqual(
            configuration["database"]["ENGINE"],
            "django.db.backends.postgresql",
        )
        self.assertEqual(configuration["database"]["PORT"], 5432)

    def test_production_rejects_debug_true(self):
        result = settings_subprocess(
            "config.settings.production",
            {"DJANGO_DEBUG": "true"},
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot be enabled in production", result.stderr)
