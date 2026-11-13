from typing import Literal, TypedDict, Any, Optional
from mptcp_reaserch_dashboard.types.common import *
from mptcp_reaserch_dashboard.types.scenario import Scenario

class Run(TypedDict):
    
    schema: Literal['mptcp-run/1']
    
    run_id: str
    
    experiment_id: Id
    
    scenario: ScenarioRunSettings
    
    environment_id: Id
    
    algorithm: AlgorithmRunSettings
    
    repetition: int
    
    seed: Seed
    
    scope: Scope
    
    snapshot: Snapshot
    
    condition_hash: Optional[Sha256]
    
    status: Literal['pending', 'running', 'completed', 'failed', 'interrupted', 'invalidated']
    
    status_reason: Optional[str]
    
    attempts: Optional[list[Attempt]]

class Attempt(TypedDict):
    
    started_utc: Timestamp
    
    finished_utc: Optional[Timestamp]
    
    outcome: Optional[Literal['completed', 'failed', 'interrupted']]
    
    exit_code: Optional[int|None]
    
    wall_s: Optional[float]

class ScenarioRunSettings(TypedDict):
    
    id: Id
    
    version: Version
    
    variant_id: str
    
    sweep_values: Optional[dict[str, Any]]

class AlgorithmRunSettings(TypedDict):
    
    id: Id
    
    profile: Optional[Id]
    
    version: Optional[str]
    
    implementation_hash: Optional[str|None]

Scope = TypedDict('Scope', {
    'class': Literal['supported', 'exploratory'],
    'reasons': list[str]
})

class Snapshot(TypedDict):
    
    scenario: Scenario # okay, bit weird
    
    expanded_events: Optional[list[Any]]
    
    algorithm: dict[str, Any]
    
    environment: dict[str, Any]