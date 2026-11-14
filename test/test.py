import mptcp_reaserch_dashboard.resource_manager as mptcp_resource
import json

with open(r"test/scenario-media-path-failure.json") as f:
    data = json.load(f)

mptcp_resource.scenario_insert(data)
print("done")