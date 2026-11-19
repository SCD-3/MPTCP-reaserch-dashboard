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
def api_algorithm_new():
    data = flask.request.json
    
    try:
        mptcp_resource.algorithm_insert(data)
    except err.InvalidResourceError:
        return 'bad data', 400
    return 'ok', 200

@app.get('/api/algorithm/<id>')
def api_algorithm_get(id: str):
    algorithm = mptcp_resource.algorithm_get(id)
    
    if algorithm is None:
        return 'not found', 404
    
    return flask.jsonify(algorithm), 200

@app.get('/api/algorithm')
def api_algorithm_get_all():
    filter = flask.request.get_json(silent=True)
    algorithms = mptcp_resource.algorithm_get_all(filter)
    
    return flask.jsonify(algorithms), 200


@app.post('/api/environment')
def api_environment_new():
    data = flask.request.json
    
    try:
        mptcp_resource.environment_insert(data)
    except err.InvalidResourceError:
        return 'bad data', 400
    return 'ok', 200

@app.get('/api/environment/<id>')
def api_environment_get(id: str):
    environment = mptcp_resource.environment_get(id)
    
    if environment is None:
        return 'not found', 404
    
    return flask.jsonify(environment), 200

@app.get('/api/environment')
def api_environment_get_all():
    filter = flask.request.get_json(silent=True)
    environments = mptcp_resource.environment_get_all(filter)
    
    return flask.jsonify(environments), 200


@app.post('/api/experiment')
def api_experiment_new():
    data = flask.request.json
    
    try:
        mptcp_resource.experiment_insert(data)
    except err.InvalidResourceError:
        return 'bad data', 400
    return 'ok', 200

@app.get('/api/experiment/<id>')
def api_experiment_get(id: str):
    try:
        version = int(flask.request.args.get('version', 0))
        if version < 0:
            raise ValueError
        
    except TypeError, ValueError:
        version = 0
        
    experiment = mptcp_resource.experiment_get(id, version)
    
    if experiment is None:
        return 'not found', 404
    
    return flask.jsonify(experiment), 200

@app.get('/api/experiment')
def api_experiment_get_all():
    filter = flask.request.get_json(silent=True)
    experiments = mptcp_resource.experiment_get_all(filter)
    
    return flask.jsonify(experiments), 200


@app.post('/api/run')
def api_run_new():
    data = flask.request.json
    
    try:
        mptcp_resource.run_insert(data)
    except err.InvalidResourceError:
        return 'bad data', 400
    return 'ok', 200

@app.get('/api/run/<path:id>')
def api_run_get(id: str):
    run = mptcp_resource.run_get(id)
    print('hello')
    
    if run is None:
        return 'not found', 404
    
    return flask.jsonify(run), 200

@app.get('/api/run')
def api_run_get_all():
    filter = flask.request.get_json(silent=True)
    runs = mptcp_resource.run_get_all(filter)
    
    return flask.jsonify(runs), 200


@app.post('/api/scenario')
def api_scenario_new():
    data = flask.request.json
    
    try:
        mptcp_resource.scenario_insert(data)
    except err.InvalidResourceError:
        return 'bad data', 400
    return 'ok', 200

@app.get('/api/scenario/<id>')
def api_scenario_get(id: str):
    try:
        version = int(flask.request.args.get('version', 0)) # type: ignore
        if version < 0:
            raise ValueError
        
    except TypeError, ValueError:
        version = 0
        
    scenario = mptcp_resource.scenario_get(id, version)
    
    if scenario is None:
        return 'not found', 404
    
    return flask.jsonify(scenario), 200

@app.get('/api/scenario')
def api_scenario_get_all():
    filter = flask.request.get_json(silent=True)
    scenarios = mptcp_resource.scenario_get_all(filter)
    
    return flask.jsonify(scenarios), 200





@app.get('/algorithm/<id>')
def algorithm_view(id: str):
    response = api_algorithm_get(id)
    
    if response[1] != 200:
        return 'not found', 404
    
    return flask.render_template('algorithms/algorithm-view.html', algorithm=response[0].json)

@app.get('/algorithm')
def algorithms_list():
    response = api_algorithm_get_all()
    
    return flask.render_template('algorithms/algorithm-list.html', algorithms=response[0].json)

@app.get('/algorithm/<id>/edit')
def algorithm_edit(id: str):
    response = api_algorithm_get(id)
    
    if response[1] != 200:
        return 'not found', 404
    
    return flask.render_template('algorithms/algorithm-edit.html', algorithm=response[0].json)



@app.get('/environment/<id>')
def environment_view(id: str):
    response = api_environment_get(id)
    
    if response[1] != 200:
        return 'not found', 404
    
    return flask.render_template('environments/environment-view.html', environment=response[0].json)

@app.get('/environment')
def environments_list():
    response = api_environment_get_all()
    
    return flask.render_template('environments/environment-list.html', environments=response[0].json)

@app.get('/environment/<id>/edit')
def environment_edit(id: str):
    response = api_environment_get(id)
    
    if response[1] != 200:
        return 'not found', 404
    
    return flask.render_template('environments/environment-edit.html', environment=response[0].json)



@app.get('/experiment/<id>')
def experiment_view(id: str):
    response = api_experiment_get(id)
    
    if response[1] != 200:
        return 'not found', 404
    
    return flask.render_template('experiments/experiment-view.html', experiment=response[0].json)

@app.get('/experiment')
def experiments_list():
    response = api_experiment_get_all()
    
    return flask.render_template('experiments/experiment-list.html', experiments=response[0].json)

@app.get('/experiment/<id>/edit')
def experiment_edit(id: str):
    response = api_experiment_get(id)
    
    if response[1] != 200:
        return 'not found', 404
    
    return flask.render_template('experiments/experiment-edit.html', experiment=response[0].json)



@app.get('/run/<path:id>')
def run_view(id: str):
    response = api_run_get(id)
    
    if response[1] != 200:
        return 'not found', 404
    
    return flask.render_template('runs/run-view.html', run=response[0].json)

@app.get('/run')
def runs_list():
    response = api_run_get_all()
    
    return flask.render_template('runs/run-list.html', runs=response[0].json)

@app.get('/run/<path:id>/edit')
def run_edit(id: str):
    response = api_run_get(id)
    
    if response[1] != 200:
        return 'not found', 404
    
    return flask.render_template('runs/run-edit.html', run=response[0].json)



@app.get('/scenario/<id>')
def scenario_view(id: str):
    response = api_scenario_get(id)
    
    if response[1] != 200:
        return 'not found', 404
    
    return flask.render_template('scenarios/scenario-view.html', scenario=response[0].json)

@app.get('/scenario')
def scenarios_list():
    scenarios = api_scenario_get_all()
    
    return flask.render_template('scenarios/scenario-list.html', scenarios=scenarios[0].json)

@app.get('/scenario/<id>/edit')
def scenario_edit(id: str):
    response = api_scenario_get(id)
    
    if response[1] != 200:
        return 'not found', 404
    
    return flask.render_template('scenarios/scenario-edit.html', scenario=response[0].json)


if __name__ == '__main__':
    app.run()