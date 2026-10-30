import flask
import json
import mptcp_reaserch_dashboard.data_manager as data

app = flask.Flask(__name__)



@app.route('/')
def index():
    return "test"

@app.route('/algorithms/<id>')
def get_algorithms(id: str):
    with open(data.DATA_BASE_PATH / data.ALGORITHMS_DATA_PATH) as file:
        return str(json.load(file)[id]['name'])

if __name__ == '__main__':
    app.run()