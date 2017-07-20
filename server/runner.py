import uuid
import signal
from subprocess import Popen
from random import random
from time import sleep

from tandem.models.flow import Flow
from tandem.utilities.web_driver import WebDriver
from tandem.utilities.job_queue_driver import WorkerDriver

class TestFailure(BaseException):
    def __init__(self, reason):
        self.reason = reason

def runner_main():
    worker_id = uuid.uuid4()
    queue_driver = WorkerDriver(worker_id)
    should_exit = False

    # Add randomness to the timeout so multiple runner instances
    # will be staggered when they unblock and re-query Redis
    timeout = 200 + int(random() * 500)

    # The runner needs to manually check to see if it should shut down
    signal.signal(signal.SIGINT, should_exit)
    signal.signal(signal.SIGTERM, should_exit)

    while not should_exit:
        maybe_flow_id = queue_driver.get_flow_job_blocking(timeout)
        if maybe_flow_id is not None:
            flow_id = int(maybe_flow_id)
            print('Received flow id: {}'.format(flow_id), flush=True)
            handle_flow(flow_id)
            queue_driver.mark_flow_job_completed(flow_id)
            print('Finished processing flow id: {}'.format(flow_id), flush=True)


def handle_flow(flow_id):
    # 1. Read from DB
    # 2. Start a new instance of headless chrome
    # 4. Run the test
    # 6. Write the result of the test
    # 7. Shutdown chrome
    chrome_cmd = ['google-chrome',
                  '--headless',
                  '--disable-gpu',
                  '--remote-debugging-port=9222']

    with Popen(chrome_cmd) as chrome:
        try:
            sleep(1)
            run(flow_id)
            # Write to DB
            # Notify server if needed
        finally:
            print('Calling chrome.terminate()', flush=True)
            chrome.terminate()

    print('Finished handling flow {}'.format(flow_id), flush=True)


def find_matching_attribute(matching_nodes, match_type, match_value, active_page):
    attributes = [active_page.get_attributes(node_id) for node_id in matching_nodes['nodeIds']]

    for node_index in range(len(attributes)):
        attrs = attributes[node_index]['attributes']
        for i in range(len(attrs) // 2):
            idx = i * 2
            if attrs[idx] == match_type and attrs[idx + 1] == match_value:
                return matching_nodes['nodeIds'][node_index]

    return None


def click(query, match_type, match_value, wait_navigate, active_page, focus=False):
    matching_nodes = active_page.query_selector_all(query)
    matches = len(matching_nodes['nodeIds'])

    if matches == 0:
        raise TestFailure('Could not find the element to click!')

    sign_in_node = matching_nodes['nodeIds'][0] if matches == 1 else \
        find_matching_attribute(matching_nodes, match_type, match_value, active_page)

    if sign_in_node is None:
        raise TestFailure('Could not find the element to click!')

    resp = active_page.resolve_node(sign_in_node)

    if 'object' not in resp or 'objectId' not in resp['object']:
        raise TestFailure ('Could not find the element to click!')

    object_id = resp['object']['objectId']

    # Perform the click
    if wait_navigate:
        active_page.enable_page_events()

    if focus:
        resp = active_page.call_function_on(object_id, 'function() { this.focus(); }')
    else:
        resp = active_page.call_function_on(object_id, 'function() { this.click(); }')

    if wait_navigate:
        active_page.wait_for('Page.frameStoppedLoading', 3)
        active_page.disable_page_events()


def type(string, active_page):
    for ch in string:
        asd = active_page.dispatch_key_event('keyDown', ch)


def page_assertion(actual_url, expected_url):
    if not actual_url == expected_url:
        raise TestFailure('Expected url did not match actual url ' + actual_url + ' <> ' + expected_url)


def run(flow):
    driver = WebDriver()
    pages = driver.pages
    page = pages[list(pages)[0]]

    try:
        with page.connect() as active_page:
            # 1. Navigate to starting page
            active_page.enable_page_events()
            active_page.goto('https://github.com')
            active_page.wait_for('Page.frameStoppedLoading', 3)
            active_page.disable_page_events()

            # 2. Run actions
            # a) Click "Sign in"
            click('a.text-bold.site-header-link', 'href', '/login', True, active_page)

            # b) Type in username
            type('geoffxy', active_page)

            # c) Focus password field
            click('#password', None, None, False, active_page, focus=True)

            # d) Type in password
            type('abc123', active_page)

            # e) Click sign in
            click('.btn.btn-primary.btn-block', 'type', 'submit', True, active_page)

            # 3. Assertion
            driver.reload_pages()
            page_assertion(page.url, 'https://github.com/session')

        # Record test passed
        print('Test passed!', flush=True)

    except TestFailure as ex:
        print('Test failed! - ' + ex.reason, flush=True)

if __name__ == '__main__':
    runner_main()
