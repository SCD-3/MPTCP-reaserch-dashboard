import pymongo
import jsonschema
import referencing
import json
import enum
from pathlib import Path

lazy import typing
lazy import pymongo.collection

lazy import mptcp_reaserch_dashboard.types as mptcp_types
lazy import mptcp_reaserch_dashboard.errors as err

type collection[T: mptcp_types.Resource] = pymongo.collection.Collection[T]

client: pymongo.MongoClient[typing.Any] = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["mptcp-database"]


algorithms: collection[mptcp_types.Algorithm]     = db['algorithms']
environments: collection[mptcp_types.Environment] = db['environments']
experiments: collection[mptcp_types.Experiment]   = db['experiments']
runs: collection[mptcp_types.Run]                 = db['runs']
scenarios: collection[mptcp_types.Scenario]       = db['scenarios']


class ResourceType(enum.Enum):
    Algorithm = enum.auto()
    Environment = enum.auto()
    Experiment = enum.auto()
    Run = enum.auto()
    Scenario = enum.auto()


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

algorithm_validator = jsonschema.Draft202012Validator(
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



def is_algorithm_valid(data: mptcp_types.Algorithm) -> bool:
    try:
        algorithm_validator.validate(data)
    except jsonschema.ValidationError:
        return False
    
    return True

def is_environment_valid(data: mptcp_types.Environment) -> bool:
    try:
        environment_validator.validate(data)
    except jsonschema.ValidationError:
        return False
    
    return True

def is_experiment_valid(data: mptcp_types.Experiment) -> bool:
    
    def lazy_check_errors():
        yield err.x_ref(data, db)
        yield err.x_profile(data, db)
        yield err.x_alg_dup(data)
        yield err.x_sweep(data)
        yield err.w_profile(data, db)
    
    try:
        experiment_validator.validate(data)
    except jsonschema.ValidationError:
        return False
    
    return not any(lazy_check_errors())

def is_run_valid(data: mptcp_types.Run) -> bool:
    try:
        run_validator.validate(data)
    except jsonschema.ValidationError:
        return False
    
    return True


def is_scenario_valid(data: mptcp_types.Scenario) -> bool:
    
    def lazy_check_errors():
        yield err.s_path_id(data)
        yield err.s_target(data)
        yield err.s_event_time(data)
        yield err.s_event_dup(data)
        yield err.s_window(data)
        yield err.s_gen(data)
        yield err.s_read(data)
        yield err.s_cross(data)
        yield err.s_pause(data)
        yield err.s_seeds(data)
    
    try:
        scenario_validator.validate(data)
    except jsonschema.ValidationError:
        return False
    
    return not any(lazy_check_errors())



def algorithm_insert(data: mptcp_types.Algorithm):
    if not is_algorithm_valid(data):
        raise err.InvalidResourceError("Algorithm is invalid")
    algorithms.insert_one(data)
    
def algorithm_get(id: str):
    return algorithms.find_one({ 'id': id })


def environment_insert(data: mptcp_types.Environment):
    if not is_environment_valid(data):
        raise err.InvalidResourceError("Environment is invalid")
    environments.insert_one(data)

def environment_get(id: str):
    return environments.find_one({ 'id': id })


def experiment_insert(data: mptcp_types.Experiment):
    if not is_experiment_valid(data):
        raise err.InvalidResourceError("Experiment is invalid")
    
    same_id = list(experiments.find({ 'id': data['id'] }))
    data['version'] = len(same_id) + 1
    
    experiments.insert_one(data)

def experiment_get(id: str):
    return experiments.find_one({ 'id': id })


def run_insert(data: mptcp_types.Run):
    if not is_run_valid(data):
        raise err.InvalidResourceError("Run is invalid")
    
    runs.insert_one(data)

def run_get(id: str):
    return runs.find_one({ 'id': id })

def scenario_insert(data: mptcp_types.Scenario):
    if not is_scenario_valid(data):
        raise err.InvalidResourceError("Scenario is invalid")
    
    same_id = list(scenarios.find({ 'id': data['id'] }))
    data['version'] = len(same_id) + 1
    
    scenarios.insert_one(data)

def scenario_get(id: str):
    return scenarios.find_one({ 'id': id })