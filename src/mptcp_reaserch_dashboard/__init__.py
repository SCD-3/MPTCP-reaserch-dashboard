import flask
import json
from pathlib import Path

import mptcp_reaserch_dashboard.data_manager as database

app = flask.Flask(__name__)
TEMPLATES_BASE_PATH = r'templates/'


@app.route('/')
def index():
    return flask.redirect(flask.url_for('get_algorithms', id="alg-lia"))



@app.post('/algorithms/<id>')
def post_algorithms(id: str):
    data = flask.request.get_json()
    # validator = database.load_schemas(database.DataKind.Algorithms)
    # validator.validate(data)
    #TODO ill have to rewrite schemas to work with single entries
    
    entry = database.Alghorithm(
        id=data['id'],
        code=data['code'],
        name=data['name'],
        short_name=data['shortName'],
        type=data['type'],
        description=data['description'],
        is_active=data['isActive'],
        parameters=data['parameters'],
        supported_environments=data['supportedEnvironments']
    )
    entry.save()
    
    return 'ok'

@app.get('/algorithms/<id>')
def get_algorithms(id: str):
    with open(database.DATA_BASE_PATH / database.ALGORITHMS_DATA_PATH) as file:
        data = json.load(file)[id]
    return flask.render_template(r'algorithm-view.html', **data)

@app.get('/environments/<id>')
def get_environments(id: str):
    with open(database.DATA_BASE_PATH / database.ENVIRONMENTS_DATA_PATH) as file:
        data = json.load(file)[id]
    return flask.render_template(r'environment-view.html', **data)

if __name__ == '__main__':
    app.run()