# pylint: disable=[missing-module-docstring, missing-class-docstring, missing-function-docstring, line-too-long]

from framework.pages.ui.base_page import BasePage


class DisappearingElementsPage(BasePage):
    # ------------------------------------------------------------------------------------------------------------------
    #                                                  Element locators
    # ------------------------------------------------------------------------------------------------------------------
    _page_heading_txt = "//h3[normalize-space()='Disappearing Elements']"

    # The nav menu items – 'Gallery' is the element that randomly disappears/reappears.
    _nav_menu_items = "//ul/li/a"
    _gallery_nav_lnk = "//ul/li/a[normalize-space()='Gallery']"

    # Static nav items that are always present
    _home_nav_lnk = "//ul/li/a[normalize-space()='Home']"
    _about_nav_lnk = "//ul/li/a[normalize-space()='About']"
    _contact_us_nav_lnk = "//ul/li/a[normalize-space()='Contact Us']"
    _portfolio_nav_lnk = "//ul/li/a[normalize-space()='Portfolio']"

    # ------------------------------------------------------------------------------------------------------------------
    #                                                      Actions
    # ------------------------------------------------------------------------------------------------------------------
    def is_page_loaded(self):
        return self.is_element_visible(self._page_heading_txt)

    def is_gallery_lnk_visible(self):
        # Use is_element_present (no wait) so the check returns immediately
        # when Gallery is absent – avoids a long wait on every refresh cycle.
        return self.is_element_present(self._gallery_nav_lnk)

    def is_home_lnk_visible(self):
        return self.is_element_visible(self._home_nav_lnk)

    def is_about_lnk_visible(self):
        return self.is_element_visible(self._about_nav_lnk)

    def is_contact_us_lnk_visible(self):
        return self.is_element_visible(self._contact_us_nav_lnk)

    def is_portfolio_lnk_visible(self):
        return self.is_element_visible(self._portfolio_nav_lnk)

    def get_nav_item_texts(self):
        """Returns a list of visible nav item texts from the menu."""
        return [item.inner_text().strip() for item in self.find_elements(self._nav_menu_items) if item.inner_text().strip()]

    def get_nav_item_count(self):
        """Returns the current count of nav menu items."""
        return self._locator(self._nav_menu_items).count()

