import os
from unittest.mock import patch

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from config.settings import environment_boolean, environment_list


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
