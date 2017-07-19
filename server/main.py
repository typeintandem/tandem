from flask import Flask

from tandem.api import api_blueprint
from tandem.client import client_blueprint

app = Flask(__name__, static_folder='../build/main')
app.register_blueprint(api_blueprint)
app.register_blueprint(client_blueprint)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
