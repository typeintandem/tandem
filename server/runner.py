import uuid
import signal
import json
from subprocess import Popen
from random import random
from time import sleep, time

from tandem.database import postgresql
from tandem.models.flow import Flow
from tandem.models.run import Run
from tandem.models.action import Action, ActionType
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
        maybe_job = queue_driver.get_flow_job_blocking(timeout)
        if maybe_job is not None:
            flow_id, run_id = maybe_job
            print('Received flow id: {}'.format(flow_id), flush=True)
            handle_flow(flow_id, run_id)
            queue_driver.mark_flow_job_completed(flow_id, run_id)
            print('Finished processing flow id: {}'.format(flow_id),
                  flush=True)


def retrieve_flow(flow_id):
    flows = [flow for flow in Flow.query.filter_by(id=flow_id)]
    actions = [action for action in Action.query.filter_by(flow_id=flow_id)]
    return flows[0], actions if len(flows) == 1 else None


def retrieve_run(run_id):
    runs = [run for run in Run.query.filter_by(id=run_id)]
    return runs[0] if len(runs) == 1 else None


def handle_flow(flow_id, run_id):
    # 1. Read from DB
    # 2. Start a new instance of headless chrome
    # 4. Run the test
    # 6. Write the result of the test
    # 7. Shutdown chrome

    flow, actions = retrieve_flow(flow_id)
    run = retrieve_run(run_id)

    if flow is None:
        print('Flow doesn\'t exist: {}'.format(flow_id), flush=True)
        return

    if run is None:
        print('Run doesn\'t exist: {}'.format(run_id), flush=True)
        return

    # Record run start time
    run.start_time = time()
    postgresql.session.add(run)
    postgresql.session.commit()

    chrome_cmd = ['google-chrome',
                  '--headless',
                  '--disable-gpu',
                  '--remote-debugging-port=9222']

    with Popen(chrome_cmd) as chrome:
        try:
            sleep(1)
            succeeded, failure_ex = run_flow(flow, actions)
            run.complete_time = time()
            if succeeded:
                print('Test passed!', flush=True)
                run.result = {'status': 'SUCCESS'}
            else:
                print('Test failed! - ' + failure_ex.reason, flush=True)
                run.result = {'status': 'FAILED'}
            postgresql.session.add(run)
            postgresql.session.commit()
        finally:
            print('Calling chrome.terminate()', flush=True)
            chrome.terminate()

    print('Finished handling flow {}'.format(flow_id), flush=True)


def find_node_with_most_matches(matching_nodes,
                                matching_attributes,
                                active_page):
    node_ids = matching_nodes['nodeIds']
    num_nodes = len(node_ids)

    attributes = [active_page.get_attributes(node_id)['attributes']
                  for node_id in node_ids]
    attribute_match_count = [0 for node_id in node_ids]
    max_index = 0

    for node_index in range(num_nodes):
        attrs = attributes[node_index]
        for i in range(len(attrs) // 2):
            idx = i * 2
            attribute_name = attrs[idx]
            attribute_value = attrs[idx + 1]
            if (attribute_name in matching_attributes and
                    attribute_value == matching_attributes[attribute_name]):
                attribute_match_count[node_index] += 1
        if (attribute_match_count[node_index] >
                attribute_match_count[max_index]):
            max_index = node_index

    return (node_ids[max_index] if attribute_match_count[max_index] > 0
            else None)


def click(query, matching_attributes, active_page):
    print('Clicking ' + query, flush=True)
    matching_nodes = active_page.query_selector_all(query)
    matches = len(matching_nodes['nodeIds'])

    if matches == 0:
        raise TestFailure('Could not find the element to click!')

    sign_in_node = matching_nodes['nodeIds'][0] if matches == 1 else \
        find_node_with_most_matches(matching_nodes,
                                    matching_attributes,
                                    active_page)

    if sign_in_node is None:
        raise TestFailure('Could not find the element to click!')

    resp = active_page.resolve_node(sign_in_node)

    if 'object' not in resp or 'objectId' not in resp['object']:
        raise TestFailure('Could not find the element to click!')

    object_id = resp['object']['objectId']

    # Perform the click
    active_page.enable_page_events()
    resp = active_page.call_function_on(object_id, 'function() { this.click(); this.focus(); }')
    active_page.wait_for('Page.frameStoppedLoading', 3)
    active_page.disable_page_events()


def type(string, active_page):
    for ch in string:
        active_page.dispatch_key_event('keyDown', ch)


def page_assertion(actual_url, expected_url):
    if not actual_url == expected_url:
        raise TestFailure('Expected url did not match actual url ' +
                          actual_url + ' <> ' + expected_url)


def run_flow(flow, actions):
    driver = WebDriver()
    pages = driver.pages
    page = pages[list(pages)[0]]

    try:
        with page.connect() as active_page:
            # Go to initial page
            active_page.enable_page_events()
            active_page.goto(flow.url)
            active_page.wait_for('Page.frameStoppedLoading', 3)
            active_page.disable_page_events()

            # Run actions
            for action in actions:
                if action.type == ActionType.click:
                    id = action.attributes['id']
                    tag = action.attributes['tagType']
                    if len(id) > 0:
                        click(id, {}, active_page)
                    else:
                        class_string = action.attributes['className'].replace(' ', '.')
                        query_string = tag.lower() + '.' + class_string
                        click(query_string, action.attributes['attributes'], active_page)

                elif action.type == ActionType.key_press:
                    type(action.attributes, active_page)

                elif action.type == ActionType.assert_url:
                    driver.reload_pages()
                    page_assertion(page.url, action.attributes)

        # Return that the test passed
        return (True, None)

    except TestFailure as ex:
        return (False, ex)


if __name__ == '__main__':
    runner_main()
