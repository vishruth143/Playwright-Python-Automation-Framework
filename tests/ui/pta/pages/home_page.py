# pylint: disable=[missing-module-docstring, missing-class-docstring, missing-function-docstring, line-too-long]

from framework.pages.ui.base_page import BasePage


class HomePage(BasePage):
    # ------------------------------------------------------------------------------------------------------------------
    #                                                  Element locators
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------Links-------------------------------------------------------
    _home_lnk = "//a[normalize-space()='Home']"
    _practice_lnk = "//a[normalize-space()='Practice']"
    _courses_lnk = "//a[normalize-space()='Courses']"
    _blog_lnk = "//a[normalize-space()='Blog']"
    _contact_lnk = "//a[normalize-space()='Contact']"

    # ------------------------------------------------------------------------------------------------------------------
    #                                                      Actions
    # ------------------------------------------------------------------------------------------------------------------
    # -----------------------------------------------------Is Visible---------------------------------------------------
    def is_on_home_page(self) -> bool:
        return self.is_url_contains("/") and "practicetestautomation.com" in self.get_current_url()

    def is_on_practice_page(self) -> bool:
        return self.is_url_contains("/practice/")

    def is_on_courses_page(self) -> bool:
        return self.is_url_contains("/courses/")

    def is_on_blog_page(self) -> bool:
        return self.is_url_contains("/blog/")

    def is_on_contact_page(self) -> bool:
        return self.is_url_contains("/contact/")

    # -----------------------------------------------------Click--------------------------------------------------------
    def click_home_lnk(self) -> None:
        self.click(self._home_lnk)

    def click_practice_lnk(self) -> None:
        self.click(self._practice_lnk)

    def click_courses_lnk(self) -> None:
        self.click(self._courses_lnk)

    def click_blog_lnk(self) -> None:
        self.click(self._blog_lnk)

    def click_contact_lnk(self) -> None:
        self.click(self._contact_lnk)
