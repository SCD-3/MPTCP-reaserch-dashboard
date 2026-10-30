import json
from jsonschema import Draft202012Validator
from pathlib import Path
from enum import Enum

import typing

JSON_SCHEMA_BASE_PATH = Path(r'json-schemas')

ALGORITHMS_SCHEMA_PATH = Path(r'algorithms.schema.jsonc')
ENVIROMENTS_SCHEMA_PATH = Path(r'enviroments.schema.jsonc')
EXPERIMENTS_SCHEMA_PATH = Path(r'experiments.schema.jsonc')
SCENARIOS_SCHEMA_PATH = Path(r'scenarios.schema.jsonc')


DATA_BASE_PATH = Path(r'database')

ALGORITHMS_DATA_PATH = Path(r'algorithms.json')
ENVIROMENTS_DATA_PATH = Path(r'enviroments.json')
EXPERIMENTS_DATA_PATH = Path(r'experiments.json')
SCENARIOS_DATA_PATH = Path(r'scenarios.json')


class DataKind(Enum):
    Algorithms = "algorithms"
    Enviroments = "enviroments"
    Experiments = "experiments"
    Scenarios = "scenarios"


class AlghorithmType(Enum):
    Reference = "REFERENCE"
    Authorial = "AUTHORIAL"

class EnviromentsType(Enum):
    OpenInternet = "OPENINTERNET",
    Uml = "UML"
    Ns3 = "NS3"
    Mathematical = "MATHEMATICAL"


def load_schemas() -> dict[DataKind, Draft202012Validator]:
    with open(JSON_SCHEMA_BASE_PATH / ALGORITHMS_SCHEMA_PATH) as file:
        SCHEMA_ALGORITHMS = json.load(file)
    
    with open(JSON_SCHEMA_BASE_PATH / ENVIROMENTS_SCHEMA_PATH) as file:
        SCHEMA_ENVIROMENTS = json.load(file)
        
    with open(JSON_SCHEMA_BASE_PATH / EXPERIMENTS_SCHEMA_PATH) as file:
        SCHEMA_EXPERIMENTS = json.load(file)
        
    with open(JSON_SCHEMA_BASE_PATH / SCENARIOS_SCHEMA_PATH) as file:
        SCHEMA_SCENARIOS = json.load(file)
    
    
    Draft202012Validator.check_schema(SCHEMA_ALGORITHMS)
    Draft202012Validator.check_schema(SCHEMA_ENVIROMENTS)
    Draft202012Validator.check_schema(SCHEMA_EXPERIMENTS)
    Draft202012Validator.check_schema(SCHEMA_SCENARIOS)
    
    return {
        DataKind.Algorithms: Draft202012Validator(SCHEMA_ALGORITHMS),
        DataKind.Enviroments: Draft202012Validator(SCHEMA_ENVIROMENTS),
        DataKind.Experiments: Draft202012Validator(SCHEMA_EXPERIMENTS),
        DataKind.Scenarios: Draft202012Validator(SCHEMA_SCENARIOS)
    }


class Alghorithm:

    def __init__(self, /, *,
                 id: str,
                 code: str,
                 name: str,
                 short_name: str,
                 type: AlghorithmType,
                 description: str,
                 is_active: bool,
                 parameters: dict[str, float],
                 supported_environments: list[Enviroment]
                 ) -> None:
        self.id = id
        self.code = code
        self.name = name
        self.short_name = short_name
        self.type = type
        self.description = description
        self.is_active = is_active
        self.parameters = parameters
        self.supported_environments = supported_environments

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            'code': self.code,
            'name': self.name,
            'shortName': self.short_name,
            'type': str(self.type),
            'description': self.description,
            'isActive': self.is_active,
            'parameters': self.parameters,
            'supportedEnvironments': [e.id for e in self.supported_environments]
        }

    def save(self) -> None:
        with open(DATA_BASE_PATH / ALGORITHMS_DATA_PATH, 'r+') as file:
            old_json = json.load(file)
            old_json[self.id] = self.to_dict()

            file.seek(0)
            json.dump(old_json, file, indent=4)
            file.truncate()


class Enviroment:

    def __init__(self, /, *,
                 id: str,
                 name: str,
                 type: EnviromentsType,
                 description: str,
                 version: str,
                 is_active: bool,
                 configuration: dict[str, str]
                 ) -> None:
        self.id = id
        self.name = name
        self.type = type
        self.description = description
        self.version = version
        self.is_active = is_active
        self.configuration = configuration

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            'name': self.name,
            'type': str(self.type),
            'description': self.description,
            'version': self.version,
            'isActive': self.is_active,
            'configuration': self.configuration
        }

    def save(self) -> None:
        with open(DATA_BASE_PATH / ENVIROMENTS_DATA_PATH, 'r+') as file:
            old_json = json.load(file)
            old_json[self.id] = self.to_dict()

            file.seek(0)
            json.dump(old_json, file, indent=4)
            file.truncate()


class TransmittionPath:

    def __init__(self, /, *,
                 name: str,
                 bandwidth_mbps: float,
                 delay_ms: float,
                 jitter_ms: float,
                 packet_loss_percent: float
                 ) -> None:
        self.name = name
        self.bandwidth_mbps = bandwidth_mbps
        self.delay_ms = delay_ms
        self.jitter_ms = jitter_ms
        self.packet_loss_percent = packet_loss_percent

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            'name': self.name,
            'bandwidthMbps': self.bandwidth_mbps,
            'delayMs': self.delay_ms,
            'jitterMs': self.jitter_ms,
            'packetLossPercent': self.packet_loss_percent
        }


class Scenario:

    def __init__(self, /, *,
                 id: str,
                 name: str,
                 description: str,
                 duration: float,
                 repetitions: int,
                 receiver_consumption_mbps: float,
                 paths: list[TransmittionPath]
                 ) -> None:
        self.id = id
        self.name = name
        self.description = description
        self.duration = duration
        self.repetitions = repetitions
        self.receiver_consumption_mbps = receiver_consumption_mbps
        self.paths = paths

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            'name': self.name,
            'description': self.description,
            'durationSeconds': self.duration,
            'repetitions': self.repetitions,
            'receiverConsumptionMbps': self.receiver_consumption_mbps,
            'paths': [path.to_dict() for path in self.paths]
        }

    def save(self) -> None:
        with open(DATA_BASE_PATH / SCENARIOS_DATA_PATH, 'r+') as file:
            old_json = json.load(file)
            old_json[self.id] = self.to_dict()

            file.seek(0)
            json.dump(old_json, file, indent=4)
            file.truncate()