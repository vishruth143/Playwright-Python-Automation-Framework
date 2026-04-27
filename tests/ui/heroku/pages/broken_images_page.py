# pylint: disable=[missing-module-docstring, missing-class-docstring, missing-function-docstring, line-too-long]

from framework.pages.ui.base_page import BasePage


class BrokenImagesPage(BasePage):
    # ------------------------------------------------------------------------------------------------------------------
    #                                                  Element locators
    # ------------------------------------------------------------------------------------------------------------------
    _page_heading_txt = "//h3[normalize-space()='Broken Images']"
    # All <img> tags inside the main content div (excludes the GitHub banner image)
    _all_content_imgs = "//div[@id='content']//img"

    # ------------------------------------------------------------------------------------------------------------------
    #                                                      Actions
    # ------------------------------------------------------------------------------------------------------------------
    def is_page_loaded(self):
        return self.is_element_visible(self._page_heading_txt)

    def get_image_report(self):
        """
        Inspects every <img> inside the content div using JavaScript's
        naturalWidth property. An image that failed to load will have
        naturalWidth == 0 even though img.complete == True.

        Returns a tuple:
            broken  : list of dicts  { src, naturalWidth }  for broken images
            valid   : list of dicts  { src, naturalWidth }  for valid images
        """
        images = self.find_elements(self._all_content_imgs)
        broken = []
        valid = []

        for img in images:
            src = img.get_attribute("src") or "(no src)"
            natural_width = img.evaluate("el => el.naturalWidth")
            entry = {"src": src, "naturalWidth": natural_width}
            if natural_width == 0:
                broken.append(entry)
            else:
                valid.append(entry)

        return broken, valid
