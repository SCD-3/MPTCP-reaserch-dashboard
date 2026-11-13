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


def is_scenario_valid(data: mptcp_types.Scenario) -> tuple[bool, list[err.ValidErrors]]:
    ... #todo

def scenario_insert(data: mptcp_types.Scenario):
    if not is_scenario_valid(data):
        raise ValueError("Scenario is invalid")
    
    same_id = list(scenarios.find({ 'id': data['id'] }))
    data['version'] = len(same_id) + 1
    
    scenarios.insert_one(data)

def scenario_get(id: str):
    return scenarios.find_one({ 'id': id })