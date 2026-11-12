from typing import Literal, TypedDict, Any, Optional
from mptcp_reaserch_dashboard.types.common import *

# algorithm.schema.json

class Algorithm(TypedDict):
    
    schema: Literal['mptcp-algorithm/1']
    
    id: Id
    
    name: str
    
    short_name: str
    
    type: Literal['reference', 'custom']
    
    description: Optional[str]
    
    is_active: bool
    
    profiles: Optional[list[Profile]]
    
    parameters_schema: Optional[Parameter]
    
    implementations: list[Implementation]

class Profile(TypedDict):
    
    id: Id
    
    status: Literal['draft', 'frozen', 'retired']
    
    label: Optional[str]
    
    description: Optional[str]
    
    parameters: Parameter

class Implementation(TypedDict):
    
    env_type: EnvType
    
    status: Literal['available', 'planned', 'unsupported']
    
    version: Optional[str]
    
    version: Optional[str|None]
    
    note: Optional[str]