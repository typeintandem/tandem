from flask import Blueprint

api_blueprint = Blueprint('api', __name__)


@api_blueprint.route('/api')
def api_handler():
    return 'You\'ve hit the api!'
