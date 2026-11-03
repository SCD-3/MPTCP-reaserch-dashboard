import flask
import json

from typing import Literal

import mptcp_reaserch_dashboard.resource_manager as resource

app = flask.Flask(__name__)
TEMPLATES_BASE_PATH = r'templates/'


def resource_not_found(
    resource_type: Literal["algorithm", "environment", "experiment", "scenario"], 
    resource_id: str|None = None
    ):
    
    if resource_type not in ("algorithm", "environment", "experiment", "scenario"): # safety check
        return (None, 404) # type: ignore
    
    return flask.render_template(f"not-found.html", resource=resource_type, resource_id=resource_id), 404


@app.get('/')
def index():
    return flask.render_template('index.html')

@app.get("/favicon.ico")
def favicon():
    
    if app.static_folder is None:
        raise OSError("Failed to find static folder")
    
    return flask.send_from_directory(app.static_folder, "favicon.ico", mimetype="image/vnd.microsoft.icon")


@app.get('/new/algorithms')
def add_algorithm_form():
    return 'not yet added', 404

@app.get('/new/environments')
def add_environment_form():
    return 'not yet added', 404

@app.get('/new/experiments')
def add_experiment_form():
    return 'not yet added', 404

@app.get('/new/scenarios')
def add_scenario_form():
    return 'not yet added', 404

@app.get('/algorithms/<id>')
def get_algorithms(id: str):
    
    try:
        with open(resource.DATA_BASE_PATH / resource.ALGORITHMS_DATA_PATH) as file:
            data = json.load(file)[id]
        return flask.render_template(r'algorithms/algorithm-view.html', **data)
    except KeyError:
        return resource_not_found('algorithm', id)

@app.get('/environments/<id>')
def get_environments(id: str):
    try:
        with open(resource.DATA_BASE_PATH / resource.ENVIRONMENTS_DATA_PATH) as file:
            data = json.load(file)[id]
        return flask.render_template(r'environments/environment-view.html', **data)
    except KeyError:
        return resource_not_found('environment', id)


@app.get('/scenarios/<id>')
def get_scenarios(id: str):
    try:
        with open(resource.DATA_BASE_PATH / resource.SCENARIOS_DATA_PATH) as file:
            data = json.load(file)[id]
        return flask.render_template(r'scenarios/scenario-view.html', **data, scenarioId = id, round=round)
    except KeyError:
        return resource_not_found('scenario', id)

@app.get('/experiments/<id>')
def get_experiments(id: str):
    try:
        with open(resource.DATA_BASE_PATH / resource.EXPERIMENTS_DATA_PATH) as file:
            data = json.load(file)[id]
        return flask.render_template(r'experiments/experiment-view.html', **data, experimentId = id)
    except KeyError:
        return resource_not_found('experiment', id)


@app.get("/algorithms")
def algorithms_list():
    with open(resource.DATA_BASE_PATH / resource.ALGORITHMS_DATA_PATH) as file:
        data = json.load(file)
    return flask.render_template("algorithms/algorithms-list.html", algorithms=data)

@app.get("/environments")
def environments_list():
    with open(resource.DATA_BASE_PATH / resource.ENVIRONMENTS_DATA_PATH) as file:
        data = json.load(file)
    return flask.render_template("environments/environments-list.html", environments=data)

@app.get("/scenarios")
def scenarios_list():
    with open(resource.DATA_BASE_PATH / resource.SCENARIOS_DATA_PATH) as file:
        data = json.load(file)
    return flask.render_template("scenarios/scenarios-list.html", scenarios=data)

@app.get("/experiments")
def experiments_list():
    with open(resource.DATA_BASE_PATH / resource.EXPERIMENTS_DATA_PATH) as file:
        data = json.load(file)
    return flask.render_template("experiments/experiments-list.html", experiments=data)

if __name__ == '__main__':
    app.run()