import json
import requests
import websocket


def send_websocket_request(url, payload):
    ws = websocket.create_connection(url)
    ws.send(payload)
    response = ws.recv()
    ws.close()
    return response


class WebPage:
    def __init__(self, page_id, page_url, websocket_url):
        self._page_id = page_id
        self._page_url = page_url
        self._websocket_url = websocket_url
        self._message_id = 0

    def _request_action(self, method, params={}):
        self._message_id += 1
        request = {
            "id": self._message_id,
            "method": method,
            "params": params,
        }
        return send_websocket_request(self._websocket_url, json.dumps(request))

    @property
    def id(self):
        return self._page_id

    @property
    def url(self):
        return self._page_url

    def copy(self, web_page):
        self._page_url = web_page._page_url

    def goto(self, url):
        response = self._request_action("Page.navigate", {"url": url})
        return response


class WebDriver:
    def __init__(self, host="localhost", port="9222"):
        self._host = host
        self._port = port
        self._driver_url = "http://{0}:{1}".format(self._host, self._port)
        self._web_pages = {}

        self.check_connection()
        self.reload_pages()

    @property
    def pages(self):
        return self._web_pages

    def check_connection(self):
        requests.get(self._driver_url)

    def reload_pages(self):
        response = requests.get("{0}/json".format(self._driver_url))
        pages = tuple(WebPage(
                page["id"],
                page["url"],
                page["webSocketDebuggerUrl"]
            ) for page in response.json() if page["type"] == "page")

        new_web_pages = {}
        for page in pages:
            if page.id in self._web_pages:
                self._web_pages[page.id].copy(page)
                new_web_pages[page.id] = self._web_pages[page.id]
            else:
                new_web_pages[page.id] = page
        self._web_pages = new_web_pages


driver = WebDriver()
pages = driver.pages
page = pages[list(pages)[0]]

print(page.url)
page.goto("https://www.facebook.com")
driver.reload_pages()
print(page.url)
page.goto("https://github.com")
