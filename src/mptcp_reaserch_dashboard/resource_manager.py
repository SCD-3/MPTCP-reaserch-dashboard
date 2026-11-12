lazy import pymongo
lazy import jsonschema
lazy import referencing
lazy import json
lazy import re as regex
lazy import itertools
lazy from pathlib import Path

lazy import typing

lazy import mptcp_reaserch_dashboard.types.scenario as mptcp_types
lazy import mptcp_reaserch_dashboard.errors as err

client: pymongo.MongoClient[mptcp_types.Scenario] = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["mptcp-database"]

scenarios    = db['scenarios']


schema_dir = Path("json-schemas")

with open(schema_dir / "common.schema.json") as f:
    common_schema = json.load(f)


with open(schema_dir / 'algorithm.schema.json') as f:
    algorithm_schema = json.load(f)
with open(schema_dir / 'environment.schema.json') as f:
    environment_schema = json.load(f)
with open(schema_dir / 'experiment.schema.json') as f:
    experiment_schema = json.load(f)
with open(schema_dir / 'run.schema.json') as f:
    run_schema = json.load(f)
with open(schema_dir / "scenario.schema.json") as f:
    scenario_schema = json.load(f)


common_registry = referencing.Registry().with_resource( # type: ignore
    common_schema["$id"],
    referencing.Resource.from_contents(common_schema)
)

scenario_validator = jsonschema.Draft202012Validator(
    algorithm_schema,
    registry=common_registry # type: ignore
)
environment_validator = jsonschema.Draft202012Validator(
    environment_schema,
    registry=common_registry # type: ignore
)
experiment_validator = jsonschema.Draft202012Validator(
    experiment_schema,
    registry=common_registry # type: ignore
)
run_validator = jsonschema.Draft202012Validator(
    run_schema,
    registry=common_registry # type: ignore
)
scenario_validator = jsonschema.Draft202012Validator(
    scenario_schema,
    registry=common_registry # type: ignore
)

def scenario_find_errors(data: mptcp_types.Scenario) -> list[err.ValidErrors]:
    
    errors: list[err.ValidErrors] = []
    
    def add_error(error: err.ValidErrors):
        if error not in errors:
            errors.append(error)
    
    # S-PATH-ID
    all_unique_paths = {i['id'] for i in data['paths'] if i['id'] != 'bottleneck'}
    if len(all_unique_paths) != len(data['paths']):
        add_error('S-PATH-ID')

    # S-TARGET
    for i in itertools.chain(data['events'], data['generators']):
        if i['target'] not in all_unique_paths:
            add_error('S-TARGET')
    
    # S-EVENT-TIME
    for event in data['events']:
        if not event['at_s'] <= data['duration_s']:
            add_error('S-EVENT-TIME')
    
    # S-EVENT-DUP
    for event1 in data['events']:
        event1 = (event1['at_s'], event1['target'], event1['action'])
        for event2 in data['events']: # O(n^2) goes brr
            event2 = (event2['at_s'], event2['target'], event2['action'])
            
            if event1 == event2:
                add_error('S-EVENT-DUP')
    
    # S-WINDOW
    start, end = data['statistics_window_s']
    if not (0 <= start < end < data['duration_s']):
        add_error('S-WINDOW')

    # S-GEN
    #TODO yea, i have no idea what they mean
    
    # S-READ
    scheldues = [i['from_s'] for i in data['receiver']['read_scheldue']]
    if scheldues[0] != 0 or scheldues != sorted(scheldues):
        add_error('S-READ')

    # S-CROSS
    cross = data['topology'].get('cross_traffic')
    if cross is not None:
        for i in cross['schedule']:
            if not (i['start_s'] < i['stop_s'] <= data['duration_s']):
                add_error('S-CROSS')
    
    # S-PAUSE
    traffic = data['traffic']
    if traffic['type'] == 'media':
        media = traffic['media']
        start, stop = media['pause_s']
        
        if not (start < stop <= data['duration_s']):
            add_error('S-PAUSE')
    
    # S-SEEDS
    deafults = data['defaults']
    if len(deafults['seeds']) != deafults['repetitions']:
        add_error('S-SEEDS')
    
    # W-WARMUP
    if data['traffic']['type'] == 'bulk' and data['statistics_window_s'][0] == 0:
        add_error('W-WARMUP')
    
    # W-DELAY-TWICE
    #TODO again, no idea what they mean. paths have no events nor gens
    
    # W-BOTTLENECK
    topology = data['topology']
    bottleneck = topology.get('bottleneck')
    if topology['mode'] == 'shared' and bottleneck is not None:
        paths_bandwidth = sum(path['bandwidth_bps'] for path in data['paths'])
        if bottleneck['bandwidth_bps'] >= paths_bandwidth:
            add_error('W-BOTTLENECK')
    
    # W-QUEUE
    for path in data['paths']:
        if path['queue_pkts'] < 10:
            add_error('W-QUEUE')
    
    return errors

def scenario_get(id: str):
    if regex.match(r'^[a-z0-9][a-z0-9_.-]{0,63}$', id) is None:
        return None
    
    return scenarios.find_one({ 'id': id })