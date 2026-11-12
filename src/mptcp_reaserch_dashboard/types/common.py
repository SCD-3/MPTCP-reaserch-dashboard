from typing import Literal, TypedDict, Optional, Any

# common.schema.json

type Id = str
"""Stable identifier of a catalogue document: lower case letters, digits, '_', '.', '-'

at most 64 characters; never reused for a different object.
    """

type Version = int
"""Version of the document. 
A saved version is immutable

editing creates version + 1.
    """

type EnvType = Literal['uml', 'dce', 'ns3', 'rpi4', 'model']
"""Environment type: uml = User-Mode Linux emulation with Linux MPTCP v0.96

dce = ns-3 DCE running the Linux 4.1 MPTCP kernel

ns3 = native ns-3 MPTCP model

rpi4 = Raspberry Pi 4 testbed (stage 6, not available yet)

model = Python/Octave mathematical model (stage 7, not available yet).
    """

type Seed = int
"""Seed of one repetition. 
All random decisions of a run (loss pattern, generated events, cross traffic) are derived from it

the same seed gives the same conditions for every algorithm.
    """

type Seeds = Sequence|SeedsExplicit

class Sequence(TypedDict):
    
    strategy: Literal["sequence"]
    
    start: Seed
    """Seed of repetition 1."""
    
    step: int
    """Seed of repetition n = start + (n - 1) * step.
    """

class SeedsExplicit(TypedDict):
    
    strategy: Literal["explicit"]
    
    values: list[Seed]
    """One seed per repetition, in repetition order. 
    Rule S-SEEDS: the length must equal the number of repetitions.
"""

type Repetitions = int
"""Number of repetitions (runs with different seeds) per algorithm and environment.
    """

type Labels = dict[str, str]
"""Free key/value tags for filtering in the UI (e.g. family, stage). 
Not interpreted by the backend.
    """

type Sha256 = str

type Timestamp = str
"""UTC time, RFC 3339 (e.g. 2026-11-09T12:00:00Z).
"""

type Parameter = dict[EnvType, dict[str, Any]]