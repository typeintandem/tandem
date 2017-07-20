import uuid
import signal
from subprocess import Popen
from random import random
from time import sleep

from tandem.models.flow import Flow
from tandem.utilities.web_driver import WebDriver
from tandem.utilities.job_queue_driver import WorkerDriver


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


def run(flow):
    driver = WebDriver()
    pages = driver.pages
    page = pages[list(pages)[0]]

    # 1. Navigate to starting page
    with page.connect() as active_page:
        resp = active_page.goto("https://github.com")
        resp2 = active_page.enable_page_events()

    # 2. Run actions

    # 3. Assertion

if __name__ == '__main__':
    runner_main()
