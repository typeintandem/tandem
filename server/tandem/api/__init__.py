from flask import Blueprint, jsonify, request
from tandem.utilities.job_queue_driver import JobSubmitDriver
from tandem.database import postgresql
from tandem.models.action import Action, ActionType
from tandem.models.flow import Flow

api_blueprint = Blueprint('api', __name__)
queue_driver = JobSubmitDriver()


@api_blueprint.route('/')
def api_handler():
    return jsonify('You\'ve hit the api!')


@api_blueprint.route('/run/<id>', methods=['GET'])
def run_flow(id):
    flow_id = int(id)
    queue_driver.submit_flow_job(flow_id)
    return jsonify({})


@api_blueprint.route('/flow', methods=['POST'])
def create_flow():
    req = request.get_json()

    flow_args = {key: req[key] for key in req.keys() if not key == 'actions'}
    new_flow = Flow(**flow_args)
    postgresql.session.add(new_flow)
    postgresql.session.flush()

    def build_action(step, action):
        if action['type']:
            action['type'] = ActionType(action['type'])
        return Action(flow_id=new_flow.id, step=step+1,  **action)

    new_actions = [build_action(step, req.get('actions')[step]) for step in range(len(req.get('actions')))]
    postgresql.session.add_all(new_actions)

    postgresql.session.commit()
    return jsonify({})


@api_blueprint.route('/flows', methods=['GET'])
def get_flows():
    return jsonify([flow.as_dict() for flow in Flow.query.all()])


@api_blueprint.route('/actions/<id>', methods=['GET'])
def get_actions(id):
    return jsonify([action.as_dict() for action in Action.query.filter_by(flow_id=id)])
