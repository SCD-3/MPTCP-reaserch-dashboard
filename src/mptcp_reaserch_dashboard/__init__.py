import flask
import mptcp_reaserch_dashboard.data_manager

app = flask.Flask(__name__)



@app.route('/')
def index():
    return "test"

app.run()