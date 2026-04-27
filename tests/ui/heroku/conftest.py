# pylint: disable=[missing-function-docstring, missing-module-docstring, redefined-outer-name, unused-argument]
# pylint: disable=[line-too-long]

# =============================================================================
# HEROKU CONFTEST – Fixtures specific to the Heroku application test suite
# =============================================================================
#
# This file is automatically loaded by pytest for every test under tests/ui/heroku/.
# It provides:
#   1. A "testdata" fixture  – loads Heroku test data from YAML config (session scope).
#
# Fixture chain:
#   tests/conftest.py              (session) – output cleanup, allure setup
#       ↓
#   tests/ui/conftest.py           (ui)      – page, browser_context, region fixtures
#       ↓
#   tests/ui/heroku/conftest.py    (this)    – Heroku testdata fixture
#       ↓
#   tests/ui/heroku/test_heroku.py           – test cases
# =============================================================================

import pytest

from config.config_parser import ConfigParser


# =============================================================================
# FIXTURE: testdata (session scope)
# =============================================================================
@pytest.fixture(scope="session")
def testdata():
    return ConfigParser.load_config("heroku_ui_test_data_config")

