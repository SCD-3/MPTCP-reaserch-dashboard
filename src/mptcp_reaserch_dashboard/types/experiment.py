from typing import Literal, TypedDict, Any, Optional
from mptcp_reaserch_dashboard.types.common import *

class Experiment(TypedDict):
    
    schema: Literal['mptcp-experiment/1']
    
    id: Id
    
    version: Optional[Version]
    
    name: str
    
    description: Optional[str]
    
    labels: Optional[Labels]
    
    scenarios: list[ScenarioEtries]
    
    environments: list[Id]
    
    algorithms: list[AlgorithmsEtries]
    
    repetitions: Optional[Repetitions|None]
    
    seeds: Optional[Seeds|None]
    
    status: Literal['draft', 'planned', 'frozen', 'running', 'completed', 'stopped', 'failed']
    
    frozen_utc: Optional[Timestamp]
    
    fingerprint: Optional[Sha256]
    
    notes: Optional[str]

class ScenarioEtries(TypedDict):
    
    id: Id
    
    version: Version
    
    sweep: Optional[list[float|str|bool|None|dict[str, Any]|list[Any]]]

class AlgorithmsEtries(TypedDict):
    
    id: Id
    
    profile: Optional[Id]
    
    parameter_overrides: Optional[dict[EnvType, dict[str, Any]]]