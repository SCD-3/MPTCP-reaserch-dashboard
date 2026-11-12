from typing import Literal, TypedDict, Any, Optional
from mptcp_reaserch_dashboard.types.common import *

class Environment(TypedDict):
    
    schema: Literal['mptcp-environment/1']
    
    id: Id
    
    type: EnvType
    
    name: str
    
    description: Optional[str]
    
    host: Optional[str]
    
    platform_profile: Optional[str]
    
    fingerprint: Optional[dict[str, str]]
    
    is_active: bool
    
    capabilities: Capability
    
    scope_notes: Optional[list[str]]

class Capability(TypedDict):
    
    max_paths: int
    
    min_paths: Optional[int]
    
    topology_modes: list[Literal['disjoint', 'shared']]
    
    cross_traffic: Optional[bool]
    
    traffic_types: list[Literal['set-loss', 'set-bandwidth', 'set-delay', 'set-queue']]
    
    generator_types: list[Literal['random-delay', 'outages']]
    
    loss_models: list[Literal['none', 'bernoulli', 'gilbert-elliott', 'list']]
    
    loss_applies_to: Optional[Literal['data', 'all']]
    
    read_schedule: Optional[bool]
    
    supported_queue_pkts_max: Optional[int]