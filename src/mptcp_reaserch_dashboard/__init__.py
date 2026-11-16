import flask
from werkzeug import http

from typing import Literal

import mptcp_reaserch_dashboard.resource_manager as mptcp_resource
import mptcp_reaserch_dashboard.errors as err


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


@app.post('/api/algorithm')
def algorithm_new():
    data = flask.request.json
    
    try:
        mptcp_resource.algorithm_insert(data)
    except err.InvalidResourceError:
        return 'bad data', 400
    return 'ok', 200

@app.get('/api/algorithm/<id>')
def algorithm_get(id: str):
    algorithm = mptcp_resource.algorithm_get(id)
    
    if algorithm is None:
        return 'not found', 404
    
    return flask.jsonify(algorithm), 200


@app.post('/api/environment')
def environment_new():
    data = flask.request.json
    
    try:
        mptcp_resource.environment_insert(data)
    except err.InvalidResourceError:
        return 'bad data', 400
    return 'ok', 200

@app.get('/api/environment/<id>')
def environment_get(id: str):
    environment = mptcp_resource.environment_get(id)
    
    if environment is None:
        return 'not found', 404
    
    return flask.jsonify(environment), 200


@app.post('/api/experiment')
def experiment_new():
    data = flask.request.json
    
    try:
        mptcp_resource.experiment_insert(data)
    except err.InvalidResourceError:
        return 'bad data', 400
    return 'ok', 200

@app.get('/api/experiment/<id>')
def experiment_get(id: str):
    experiment = mptcp_resource.experiment_get(id)
    
    if experiment is None:
        return 'not found', 404
    
    return flask.jsonify(experiment), 200


@app.post('/api/run')
def run_new():
    data = flask.request.json
    
    try:
        mptcp_resource.run_insert(data)
    except err.InvalidResourceError:
        return 'bad data', 400
    return 'ok', 200

@app.get('/api/run/<id>')
def run_get(id: str):
    run = mptcp_resource.run_get(id)
    
    if run is None:
        return 'not found', 404
    
    return flask.jsonify(run), 200


@app.post('/api/scenario')
def scenario_new():
    data = flask.request.json
    
    try:
        mptcp_resource.scenario_insert(data)
    except err.InvalidResourceError:
        return 'bad data', 400
    return 'ok', 200

@app.get('/api/scenario/<id>')
def scenario_get(id: str):
    scenario = mptcp_resource.scenario_get(id)
    
    if scenario is None:
        return 'not found', 404
    
    return flask.jsonify(scenario), 200


if __name__ == '__main__':
    app.run()