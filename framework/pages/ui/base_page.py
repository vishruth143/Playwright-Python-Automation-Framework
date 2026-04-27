# pylint: disable=[missing-module-docstring, missing-class-docstring, missing-function-docstring, line-too-long]

from playwright.sync_api import Page, Locator, expect, TimeoutError as PlaywrightTimeoutError


class BasePage:
    """
    Base page class for all Playwright page objects.

    Wraps the Playwright Page object and provides a consistent interface that
    mirrors the Selenium BasePage API so that page objects require minimal changes.

    Key differences from Selenium BasePage:
      - No explicit WebDriverWait / expected_conditions needed.
        Playwright auto-waits for elements to be actionable before every interaction.
      - Locators are expressed as CSS selectors or XPath strings (prefixed with 'xpath=').
      - `find_element`  returns a Playwright Locator (lazy – no network call yet).
      - `find_elements` returns a list of Locator objects obtained via `locator.all()`.
    """

    def __init__(self, page: Page, timeout: int = 10_000):
        """
        :param page:    Playwright Page instance injected from the fixture.
        :param timeout: Default timeout in milliseconds (Playwright uses ms, not seconds).
        """
        self.page = page
        self.timeout = timeout  # milliseconds

    # ------------------------------------------------------------------------------------------------------------------
    #                                              Locator helpers
    # ------------------------------------------------------------------------------------------------------------------

    def _locator(self, selector: str) -> Locator:
        """
        Return a Playwright Locator for the given selector string.
        XPath selectors must be prefixed with 'xpath=' when passed directly to
        page.locator(); this helper adds the prefix automatically if the selector
        starts with '//'.
        """
        if selector.startswith("//") or selector.startswith("(//"):
            return self.page.locator(f"xpath={selector}")
        return self.page.locator(selector)

    # ------------------------------------------------------------------------------------------------------------------
    #                                           Core element methods
    # ------------------------------------------------------------------------------------------------------------------

    def find_element(self, selector: str) -> Locator:
        """
        Return a Locator for the given selector.
        Playwright is lazy: no DOM query happens until an action is called on the locator.
        Use `wait_for_visible` / `wait_for_attached` if you need to confirm the element
        exists before continuing.
        """
        return self._locator(selector)

    def find_elements(self, selector: str) -> list[Locator]:
        """
        Return all matching elements as a list of Locators.
        Waits until at least one element is present (up to self.timeout).
        """
        locator = self._locator(selector)
        try:
            locator.first.wait_for(state="attached", timeout=self.timeout)
        except PlaywrightTimeoutError as e:
            raise Exception(f"Elements not found: '{selector}' | Exception: {str(e)}")
        return locator.all()

    # ------------------------------------------------------------------------------------------------------------------
    #                                         Visibility / presence checks
    # ------------------------------------------------------------------------------------------------------------------

    def is_element_present(self, selector: str) -> bool:
        """Return True if at least one matching element exists in the DOM."""
        return self._locator(selector).count() > 0

    def is_element_visible(self, selector: str) -> bool:
        """Return True if the element is visible (rendered and not hidden)."""
        try:
            self._locator(selector).wait_for(state="visible", timeout=self.timeout)
            return True
        except PlaywrightTimeoutError:
            return False

    # ------------------------------------------------------------------------------------------------------------------
    #                                           Interaction methods
    # ------------------------------------------------------------------------------------------------------------------

    def click(self, selector: str) -> None:
        """Click the element identified by selector. Playwright auto-waits for actionable."""
        try:
            self._locator(selector).click(timeout=self.timeout)
        except PlaywrightTimeoutError as e:
            raise Exception(f"Element not clickable: '{selector}' | Exception: {str(e)}")

    def type_text(self, selector: str, text: str) -> None:
        """Clear the element and type text into it."""
        try:
            locator = self._locator(selector)
            locator.wait_for(state="visible", timeout=self.timeout)
            locator.clear()
            locator.fill(text)
        except PlaywrightTimeoutError as e:
            raise Exception(f"Element not found for typing: '{selector}' | Exception: {str(e)}")

    def get_text(self, selector: str) -> str:
        """Return the inner text of the element."""
        try:
            return self._locator(selector).inner_text(timeout=self.timeout)
        except PlaywrightTimeoutError as e:
            raise Exception(f"Element not found for get_text: '{selector}' | Exception: {str(e)}")

    def get_attribute(self, selector: str, attribute: str) -> str | None:
        """Return the value of the given attribute on the element."""
        try:
            return self._locator(selector).get_attribute(attribute, timeout=self.timeout)
        except PlaywrightTimeoutError as e:
            raise Exception(f"Element not found for get_attribute: '{selector}' | Exception: {str(e)}")

    # ------------------------------------------------------------------------------------------------------------------
    #                                              Wait helpers
    # ------------------------------------------------------------------------------------------------------------------

    def wait_until_not_visible(self, selector: str) -> None:
        """Wait until the element is hidden or removed from the DOM."""
        try:
            self._locator(selector).wait_for(state="hidden", timeout=self.timeout)
        except PlaywrightTimeoutError as e:
            raise Exception(f"Element still visible after timeout: '{selector}' | Exception: {str(e)}")

    def wait_for_clickable(self, selector: str) -> Locator:
        """Wait until the element is visible and enabled (actionable)."""
        try:
            locator = self._locator(selector)
            locator.wait_for(state="visible", timeout=self.timeout)
            return locator
        except PlaywrightTimeoutError as e:
            raise Exception(f"Element not clickable: '{selector}' | Exception: {str(e)}")

    # ------------------------------------------------------------------------------------------------------------------
    #                                              Page-level helpers
    # ------------------------------------------------------------------------------------------------------------------

    def get_current_url(self) -> str:
        return self.page.url

    def get_page_title(self) -> str:
        return self.page.title()

    def is_url_contains(self, partial_url: str) -> bool:
        """Return True if the current page URL contains the given string."""
        try:
            expect(self.page).to_have_url(
                # Use a regex that matches a partial URL
                __import__("re").compile(f".*{__import__('re').escape(partial_url)}.*"),
                timeout=self.timeout
            )
            return True
        except (AssertionError, PlaywrightTimeoutError):
            return False
