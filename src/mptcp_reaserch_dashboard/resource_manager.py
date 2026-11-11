import pymongo
import jsonschema
import referencing
import json
from pathlib import Path

import mptcp_reaserch_dashboard.types.scenario as mptcp_types

client: pymongo.MongoClient[mptcp_types.Scenario] = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["mptcp-database"]


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