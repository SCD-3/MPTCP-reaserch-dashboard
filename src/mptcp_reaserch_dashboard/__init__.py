import flask
import json
from pathlib import Path

import mptcp_reaserch_dashboard.data_manager as database

app = flask.Flask(__name__)
TEMPLATES_BASE_PATH = r'templates/'


@app.route('/')
def index():
    return "test"

@app.route('/algorithms/<id>')
def get_algorithms(id: str):
    with open(database.DATA_BASE_PATH / database.ALGORITHMS_DATA_PATH) as file:
        data = json.load(file)[id]
    return flask.render_template(r'algorithm-view.html', **data)

@app.route('/environments/<id>')
def get_environments(id: str):
    with open(database.DATA_BASE_PATH / database.ENVIRONMENTS_DATA_PATH) as file:
        data = json.load(file)[id]
    return flask.render_template(r'environment-view.html', **data)

if __name__ == '__main__':
    app.run()