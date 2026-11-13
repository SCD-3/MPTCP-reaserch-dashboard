import flask
import json
import jsonschema.exceptions
from werkzeug import http

from typing import Literal

import mptcp_reaserch_dashboard.resource_manager as mptcp_resource


app = flask.Flask(__name__)
TEMPLATES_BASE_PATH = r'templates/'

@app.get('/')
def index():
    return flask.render_template('index.html')

@app.get("/favicon.ico")
def favicon():
    
    if app.static_folder is None:
        raise OSError("Failed to find static folder")
    
    return flask.send_from_directory(app.static_folder, "favicon.ico", mimetype="image/vnd.microsoft.icon")


@app.post('/algorithm_new')
def algorithm_new():
    data = flask.request.json
    
    try:
        mptcp_resource.algorithm_insert(data)
    except ValueError:
        return 'bad data', 400
    return 'ok', 200

@app.post('/environment_new')
def environment_new():
    data = flask.request.json
    
    try:
        mptcp_resource.environment_insert(data)
    except ValueError:
        return 'bad data', 400
    return 'ok', 200

@app.post('/experiment_new')
def experiment_new():
    data = flask.request.json
    
    try:
        mptcp_resource.experiment_insert(data)
    except ValueError:
        return 'bad data', 400
    return 'ok', 200

@app.post('/run_new')
def run_new():
    data = flask.request.json
    
    try:
        mptcp_resource.run_insert(data)
    except ValueError:
        return 'bad data', 400
    return 'ok', 200

@app.post('/scenario_new')
def scenario_new():
    data = flask.request.json
    
    try:
        mptcp_resource.scenario_insert(data)
    except ValueError:
        return 'bad data', 400
    return 'ok', 200


if __name__ == '__main__':
    app.run()