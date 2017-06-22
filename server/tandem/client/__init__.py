from flask import Blueprint

client_blueprint = Blueprint('client', __name__)


@client_blueprint.route('/')
def index_handler():
    return "You've hit index!"


@client_blueprint.route('/client')
def client_handler():
    return "You've hit the client!"
