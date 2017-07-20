import json
import requests
import websocket
from threading import Thread, Semaphore, Lock, Condition


class Connection:
    def __init__(self, websocket_url):
        self._websocket_url = websocket_url
        self._message_id = 0
        self._ws = None
        self._read_thread = None

        self._pending_requests = {}
        self._pending_requests_lock = Lock()

        self._waiting_events = {}
        self._waiting_events_lock = Lock()

    def __enter__(self):
        self._ws = websocket.create_connection(self._websocket_url)
        self._recv_thread = Thread(target = self._handle_messages)
        self._recv_thread.start()
        return self

    def __exit__(self, *args):
        self._ws.close()
        self._recv_thread.join()
        self._ws = None

    def _handle_messages(self):
        try:
            while True:
                message = json.loads(self._ws.recv())
                if 'id' in message:
                    # Response
                    request_id = message['id']
                    with self._pending_requests_lock:
                        if request_id in self._pending_requests:
                            response_list, cond = self._pending_requests[request_id]
                            response_list.append(message['result'])
                            cond.release()
                        else:
                            print('Received a message with id {} that has no waiting thread'.format(request_id), flush=True)
                elif 'method' in message:
                    # Event
                    event_name = message['method']
                    with self._waiting_events_lock:
                        if event_name in self._waiting_events:
                            self._waiting_events[event_name].notify_all()
                else:
                    pass
        except:
            pass

    def _request(self, method, params={}):
        request_id = self._message_id
        self._message_id += 1

        request = {
            "id": request_id,
            "method": method,
            "params": params,
        }

        # Condition used to wait for response
        cond = Semaphore(0)

        # Store pending request
        with self._pending_requests_lock:
            self._pending_requests[request_id] = ([], cond)

        # Actually send the request
        self._ws.send(json.dumps(request))

        # Wait for a response
        cond.acquire()

        response = None

        # Extract the response
        with self._pending_requests_lock:
            response = self._pending_requests[request_id][0][0]
            self._pending_requests.pop(request_id, None)

        return response

    def wait_for(self, event_name, timeout):
        with self._waiting_events_lock:
            cond = None
            if event_name not in self._waiting_events:
                self._waiting_events[event_name] = Condition(self._waiting_events_lock)
            self._waiting_events[event_name].wait(timeout)

    def goto(self, url):
        return self._request('Page.navigate', {'url': url})

    def enable_page_events(self):
        return self._request('Page.enable', {})

    def disable_page_events(self):
        return self._request('Page.disable', {})

    def query_selector_all(self, query):
        document_dom = self._request('DOM.getDocument', {})
        root_node_id = document_dom['root']['nodeId']
        return self._request('DOM.querySelectorAll', {'nodeId': root_node_id, 'selector': query})

    def get_attributes(self, node_id):
        return self._request('DOM.getAttributes', {'nodeId': node_id})

    def resolve_node(self, node_id):
        return self._request('DOM.resolveNode', {'nodeId': node_id})

    def call_function_on(self, object_id, function):
        return self._request('Runtime.callFunctionOn', {'objectId': object_id, 'functionDeclaration': function})

    def dispatch_key_event(self, type, text):
        return self._request('Input.dispatchKeyEvent', {'type': type, 'text': text})

    def get_navigation_history(self):
        return self._request('Page.getNavigationHistory', {})


class WebPage:
    def __init__(self, page_id, page_url, websocket_url):
        self._page_id = page_id
        self._page_url = page_url
        self._websocket_url = websocket_url

    @property
    def id(self):
        return self._page_id

    @property
    def url(self):
        return self._page_url

    def copy(self, web_page):
        self._page_url = web_page._page_url

    def connect(self):
        return Connection(self._websocket_url)

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
                page["webSocketDebuggerUrl"] if 'webSocketDebuggerUrl' in page else None
            ) for page in response.json() if page["type"] == "page")

        new_web_pages = {}
        for page in pages:
            if page.id in self._web_pages:
                self._web_pages[page.id].copy(page)
                new_web_pages[page.id] = self._web_pages[page.id]
            else:
                new_web_pages[page.id] = page
        self._web_pages = new_web_pages
