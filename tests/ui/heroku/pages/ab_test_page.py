# pylint: disable=[missing-module-docstring, missing-class-docstring, missing-function-docstring, line-too-long]

from framework.pages.ui.base_page import BasePage


class ABTestPage(BasePage):
    # ------------------------------------------------------------------------------------------------------------------
    #                                                  Element locators
    # ------------------------------------------------------------------------------------------------------------------
    _ab_test_control_heading_txt = "//h3[normalize-space()='A/B Test Control']"
    _ab_test_variation_heading_txt = "//h3[normalize-space()='A/B Test Variation 1']"
    _ab_test_description_txt = "//p[contains(text(),'split testing')]"

    # ------------------------------------------------------------------------------------------------------------------
    #                                                      Actions
    # ------------------------------------------------------------------------------------------------------------------
    def is_ab_test_page_loaded(self):
        """Returns True if either the Control or Variation 1 heading is visible."""
        return (
            self.is_element_visible(self._ab_test_control_heading_txt)
            or self.is_element_visible(self._ab_test_variation_heading_txt)
        )

    def is_description_visible(self):
        return self.is_element_visible(self._ab_test_description_txt)

    def get_heading_text(self):
        """Returns the visible heading text regardless of which variant is served."""
        if self.is_element_visible(self._ab_test_control_heading_txt):
            return self.get_text(self._ab_test_control_heading_txt)
        if self.is_element_visible(self._ab_test_variation_heading_txt):
            return self.get_text(self._ab_test_variation_heading_txt)
        return ""

