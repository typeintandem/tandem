from flask import Flask

from tandem.api import api_blueprint
from tandem.client import client_blueprint
from tandem.database import postgresql

app = Flask(__name__, static_folder='../build/main')
app.register_blueprint(api_blueprint, url_prefix='/api')
app.register_blueprint(client_blueprint)


@app.teardown_appcontext
def shutdown_session(exception=None):
    postgresql.session.remove()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
