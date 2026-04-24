from playwright.sync_api import Page

def test_playwright_fixture(playwright):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    try:
        page = context.new_page()
        page.goto("https://www.google.com", wait_until="domcontentloaded")
        title = page.title()
        assert "Google" in title, f"Actual title: {title}"
    finally:
        context.close()
        browser.close()

# Page fixture by default have chromium with headless mode and 1 single context
def test_playwright_page_fixture(page:Page):
    try:
        page.goto("https://www.google.com", wait_until="domcontentloaded")
        title = page.title()
        assert "Google" in title, f"Actual title: {title}"
    finally:
        page.close()

'''
-------------------------------------------------------------------------------------
    Attribute                       |   Locator Syntax          |   Example         |
-------------------------------------------------------------------------------------
    id                              |   #idname                 |   #username       |
                                    |   tagname#idname          |   input#username  |
    classname                       |   .classname              |   .search-keyword |
                                    |   tagname.classname       |   button.submit   |
    Customized with any attribute   |   tagname[attribute=value]|   input[type=text]|
    tagnames                        |   form input              |   form input      |
-------------------------------------------------------------------------------------
'''
def test_core_locators(page:Page):
    page.goto("https://rahulshettyacademy.com/loginpagePractise/")
    page.get_by_label("Username:").fill("rahulshettyacademy")
    page.get_by_label("Password:").fill("Learning@830$3mK2")
    page.get_by_role("combobox").select_option("Teacher")
    page.locator("#terms").check()
    page.get_by_role("link", name="terms and conditions").click()
    page.get_by_role("button", name="Sign In").click()
