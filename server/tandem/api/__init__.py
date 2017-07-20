from flask import Blueprint
from tandem.utilities.job_queue_driver import JobSubmitDriver

api_blueprint = Blueprint('api', __name__)
queue_driver = JobSubmitDriver()


@api_blueprint.route('/api')
def api_handler():
    return 'You\'ve hit the api!'


@api_blueprint.route('/submit/<id>')
def submit_job_handler(id):
    flow_id = int(id)
    queue_driver.submit_flow_job(flow_id)
    return 'Submitted!'
