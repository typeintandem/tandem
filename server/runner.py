from tandem.models.flow import Flow
from tandem.utilities.web_driver import WebDriver


def run(flow):
    driver = WebDriver()
    pages = driver.pages
    page = pages[list(pages)[0]]

    print(page.url)
    page.goto("https://www.facebook.com")
    driver.reload_pages()
    print(page.url)
    page.goto("https://github.com")


if __name__ == "__main__":
    flow_ids = [1, 2, 3]
    print([run(flow) for flow in Flow.get_by_ids(flow_ids)])
