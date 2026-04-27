# pylint: disable=[missing-module-docstring, missing-class-docstring, missing-function-docstring, line-too-long, broad-exception-caught]

from framework.pages.ui.base_page import BasePage


class AddRemoveElementsPage(BasePage):
    # ------------------------------------------------------------------------------------------------------------------
    #                                                  Element locators
    # ------------------------------------------------------------------------------------------------------------------
    _add_element_btn = "//button[normalize-space()='Add Element']"
    _delete_btns = "//button[normalize-space()='Delete']"
    _page_heading_txt = "//h3[normalize-space()='Add/Remove Elements']"

    # ------------------------------------------------------------------------------------------------------------------
    #                                                      Actions
    # ------------------------------------------------------------------------------------------------------------------
    def is_page_loaded(self):
        return self.is_element_visible(self._page_heading_txt)

    def is_add_element_btn_visible(self):
        return self.is_element_visible(self._add_element_btn)

    def is_delete_btn_visible(self):
        return self.is_element_visible(self._delete_btns)

    def get_delete_btn_count(self):
        """Returns the current number of Delete buttons present on the page."""
        try:
            return self._locator(self._delete_btns).count()
        except Exception:
            return 0

    def click_add_element_btn(self):
        self.click(self._add_element_btn)

    def click_first_delete_btn(self):
        self._locator(self._delete_btns).first.click(timeout=self.timeout)
