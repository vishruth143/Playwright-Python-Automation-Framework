# pylint: disable=[missing-module-docstring, missing-class-docstring, missing-function-docstring, line-too-long]

from framework.pages.ui.base_page import BasePage


class LoginPage(BasePage):
    # ------------------------------------------------------------------------------------------------------------------
    #                                                  Element locators
    # ------------------------------------------------------------------------------------------------------------------
    # ---------------------------------------------------Input Fields---------------------------------------------------
    _username_input = "#username"
    _password_input = "#password"

    # -----------------------------------------------------Buttons------------------------------------------------------
    _submit_btn = "#submit"
    _logout_btn = "//a[normalize-space()='Log out']"

    # ------------------------------------------------------Texts-------------------------------------------------------
    _logged_in_successfully_txt = "//h1[normalize-space()='Logged In Successfully']"

    # ------------------------------------------------------Links-------------------------------------------------------
    _test_login_page_lnk = "//a[normalize-space()='Test Login Page']"
    _test_exceptions_lnk = "//a[normalize-space()='Test Exceptions']"

    # ------------------------------------------------------------------------------------------------------------------
    #                                                      Actions
    # ------------------------------------------------------------------------------------------------------------------
    # -----------------------------------------------------Is Visible---------------------------------------------------
    def username_input_visible(self) -> bool:
        return self.is_element_visible(self._username_input)

    def logged_in_successfully_txt_visible(self) -> bool:
        return self.is_element_visible(self._logged_in_successfully_txt)

    # -----------------------------------------------------Enter/Type---------------------------------------------------
    def type_username_input(self, username: str) -> None:
        self.type_text(self._username_input, username)

    def type_password_input(self, password: str) -> None:
        self.type_text(self._password_input, password)

    # -----------------------------------------------------Click--------------------------------------------------------
    def click_submit_btn(self) -> None:
        self.click(self._submit_btn)

    def click_logout_btn(self) -> None:
        self.click(self._logout_btn)

    def click_test_login_page_lnk(self) -> None:
        self.click(self._test_login_page_lnk)

    def click_test_exception_lnk(self) -> None:
        self.click(self._test_exceptions_lnk)
