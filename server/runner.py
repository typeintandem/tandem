import uuid
import signal

from random import random
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
            # Read from DB
            # Run test
            queue_driver.mark_flow_job_completed(flow_id)


def run(flow):
    driver = WebDriver()
    pages = driver.pages
    page = pages[list(pages)[0]]

    print(page.url)
    page.goto("https://www.facebook.com")
    driver.reload_pages()
    print(page.url)
    page.goto("https://github.com")


if __name__ == '__main__':
    runner_main()
