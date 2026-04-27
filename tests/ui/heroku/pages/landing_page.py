# pylint: disable=[missing-module-docstring, missing-class-docstring, missing-function-docstring, line-too-long]

from framework.pages.ui.base_page import BasePage


class LandingPage(BasePage):
    # ------------------------------------------------------------------------------------------------------------------
    #                                                  Element locators
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------Texts-------------------------------------------------------
    _page_heading_txt = "//h1[normalize-space()='Welcome to the-internet']"

    # ------------------------------------------------------Links-------------------------------------------------------
    _all_example_lnks = "//ul/li/a"
    _ab_testing_lnk = "//a[normalize-space()='A/B Testing']"
    _add_remove_elements_lnk = "//a[normalize-space()='Add/Remove Elements']"
    _basic_auth_lnk = "//a[normalize-space()='Basic Auth']"
    _broken_images_lnk = "//a[normalize-space()='Broken Images']"
    _challenging_dom_lnk = "//a[normalize-space()='Challenging DOM']"
    _digest_auth_lnk = "//a[normalize-space()='Digest Authentication']"
    _disappearing_elements_lnk = "//a[normalize-space()='Disappearing Elements']"

    # ------------------------------------------------------------------------------------------------------------------
    #                                                      Actions
    # ------------------------------------------------------------------------------------------------------------------
    def is_landing_page_loaded(self):
        return self.is_element_visible(self._page_heading_txt)

    def get_all_links(self):
        """
        Returns a list of dicts for every <a> element on the landing page.
        Each dict contains:
          - text  : visible link text
          - href  : absolute href attribute value
        """
        links = []
        for element in self.find_elements(self._all_example_lnks):
            href = element.get_attribute("href") or ""
            text = (element.inner_text() or "").strip()
            if href:
                links.append({"text": text, "href": href})
        return links

    def click_ab_testing_lnk(self):
        self.click(self._ab_testing_lnk)

    def click_add_remove_elements_lnk(self):
        self.click(self._add_remove_elements_lnk)

    def click_basic_auth_lnk(self):
        self.click(self._basic_auth_lnk)

    def click_broken_images_lnk(self):
        self.click(self._broken_images_lnk)

    def click_challenging_dom_lnk(self):
        self.click(self._challenging_dom_lnk)

    def click_digest_auth_lnk(self):
        self.click(self._digest_auth_lnk)

    def click_disappearing_elements_lnk(self):
        self.click(self._disappearing_elements_lnk)

