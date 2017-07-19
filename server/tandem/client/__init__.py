from flask import Blueprint, render_template

client_blueprint = Blueprint('client', __name__, template_folder='templates')


@client_blueprint.route('/')
def index_handler():
    return render_template('index.html')
