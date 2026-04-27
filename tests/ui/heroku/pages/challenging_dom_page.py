# pylint: disable=[missing-module-docstring, missing-class-docstring, missing-function-docstring, line-too-long]

from framework.pages.ui.base_page import BasePage


class ChallengingDomPage(BasePage):
    # ------------------------------------------------------------------------------------------------------------------
    #                                                  Element locators
    # ------------------------------------------------------------------------------------------------------------------
    # The three action buttons share the "button" class; alert = red, success = green, plain = blue
    _blue_btn = "//a[contains(@class,'button') and not(contains(@class,'alert')) and not(contains(@class,'success'))]"
    _red_btn = "//a[contains(@class,'button alert')]"
    _green_btn = "//a[contains(@class,'button success')]"

    _page_heading_txt = "//h3[normalize-space()='Challenging DOM']"
    _table_header_cells = "//table/thead/tr/th"
    _table_body_rows = "//table/tbody/tr"
    # First cell of the first body row – used to detect DOM regeneration
    _first_row_first_cell = "//table/tbody/tr[1]/td[1]"

    # ------------------------------------------------------------------------------------------------------------------
    #                                                      Actions
    # ------------------------------------------------------------------------------------------------------------------
    def is_page_loaded(self):
        return self.is_element_visible(self._page_heading_txt)

    def get_table_headers(self):
        """Returns a list of visible header texts from the table."""
        return [cell.inner_text().strip() for cell in self.find_elements(self._table_header_cells)]

    def get_table_row_count(self):
        """Returns the number of body rows in the table."""
        return self._locator(self._table_body_rows).count()

    def get_first_row_text(self):
        """Returns the text of the first cell in the first table body row."""
        return self.find_element(self._first_row_first_cell).inner_text().strip()

    def get_blue_btn_id(self):
        """Returns the 'id' attribute of the blue button (regenerated on each click)."""
        return self.get_attribute(self._blue_btn, "id") or ""

    def get_red_btn_id(self):
        """Returns the 'id' attribute of the red button (regenerated on each click)."""
        return self.get_attribute(self._red_btn, "id") or ""

    def get_green_btn_id(self):
        """Returns the 'id' attribute of the green button (regenerated on each click)."""
        return self.get_attribute(self._green_btn, "id") or ""

    def wait_for_table_to_regenerate(self, initial_first_cell_text: str, timeout: int = 10_000) -> bool:
        """
        Waits until the first cell of the first body row changes its text,
        which confirms the table was re-rendered by a button click.

        In Playwright there are no stale element exceptions; instead we poll
        until the cell text differs from the captured pre-click value.

        Returns True if regeneration detected within timeout, False otherwise.
        """
        try:
            self.page.wait_for_function(
                f"() => document.querySelector('table tbody tr:first-child td:first-child')?.innerText?.trim() !== {repr(initial_first_cell_text)}",
                timeout=timeout,
            )
            return True
        except Exception:  # pylint: disable=broad-except
            return False

    def click_blue_btn(self):
        self.click(self._blue_btn)

    def click_red_btn(self):
        self.click(self._red_btn)

    def click_green_btn(self):
        self.click(self._green_btn)

