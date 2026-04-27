# pylint: disable=[line-too-long, missing-module-docstring, missing-function-docstring, missing-class-docstring]
# pylint: disable=[unused-variable, import-error]

import random
from datetime import datetime, timezone

from faker import Faker
from playwright.sync_api import Page

from config.config_parser import ConfigParser
from tests.ui.pta.pages.login_page import LoginPage


class Common:
    """
    Reusable helper methods shared across test suites.

    Playwright equivalent of the Selenium Common class.  Keyboard shortcuts
    (copy/paste/scroll) are handled natively by Playwright via page.keyboard
    and locator.press(), so only the methods actually used in tests are kept.
    """

    # ------------------------------------------------------------------------------------------------------------------
    #                                          Static data-generation helpers
    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def fake_name() -> str:
        return Faker().name()

    @staticmethod
    def fake_first_name() -> str:
        return Faker().first_name()

    @staticmethod
    def fake_last_name() -> str:
        return Faker().last_name()

    @staticmethod
    def fake_ssn() -> str:
        return Faker().ssn().replace('-', '')

    @staticmethod
    def fake_phonenumber() -> str:
        return str(random.randint(2220000000, 2229999999))

    @staticmethod
    def get_date() -> str:
        return datetime.now(timezone.utc).strftime('%m-%d-%Y')

    # ------------------------------------------------------------------------------------------------------------------
    #                                          Instance helpers
    # ------------------------------------------------------------------------------------------------------------------

    def __init__(self, page: Page, test_data=None):
        self.page = page
        self.test_data = test_data
        self.loginpage = LoginPage(self.page)

    def pta_login(self, region: str) -> None:
        """
        Log in to the PTA application using credentials from the env config.

        :param region: Environment key (e.g. "QA", "DEV").
        """
        ui_test_env_config = ConfigParser.load_config("pta_ui_test_env_config")
        env_config = ui_test_env_config.get(region.upper(), {})

        username = env_config.get("username")
        password = env_config.get("password")

        self.loginpage.type_username_input(username)
        self.loginpage.type_password_input(password)
        self.loginpage.click_submit_btn()

    def pta_logout(self) -> None:
        """Log out of the PTA application."""
        self.loginpage.click_logout_btn()

