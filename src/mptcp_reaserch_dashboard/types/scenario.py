from typing import Literal, TypedDict, Any, Optional
from mptcp_reaserch_dashboard.types.common import *

# scenario.schema.json

class Scenario(TypedDict):
    
    schema: Literal["mptcp-scenario/1"]
    
    id: Id
    
    version: Version
    
    name: str
    """Short human-readable title."""
    
    description: str
    """Purpose of the test and what is expected to happen."""
    
    labels: Labels
    
    duration_s: int
    """Duration of the data transfer in one run, from the sender start."""
    
    statistics_window_s: tuple[int, int]
    """[from, to] time window used for summary metrics; the part before 'from' is warm-up (slow start). Rule S-WINDOW: 0 <= from < to <= duration_s. Default when omitted: [5, duration_s] (or [0, duration_s] for runs shorter than 10 s)."""

    topology: Topology
    
    paths: list[Path]
    """Network paths between client and server, one MPTCP subflow each. The format allows up to 8; every current environment supports exactly 2 (see the environment's capabilities.max_paths). Rule S-PATH-ID: ids unique."""
    
    events: list[Event]
    """Timed changes of path or bottleneck parameters. Rules S-TARGET, S-EVENT-TIME, S-EVENT-DUP."""
    
    generators: list[Generator]
    """Randomised series of changes. They are expanded into concrete events per seed when the experiment is frozen, so every algorithm sees the same series. Rules S-TARGET, S-GEN."""
    
    traffic: Traffic
    
    sender: Sender
    
    receiver: Receiver
    
    defaults: Defaults
    
    backend_overrides: BackendOverrides

class Sender(TypedDict):
    """Fixed send buffer (SO_SNDBUF). 0 = the platform's autotuning."""
    
    sndbuf_bytes: int # ???

class Defaults(TypedDict):
    """Default repetition plan. An experiment may override both values."""
    
    repetitions: Repetitions
    
    seeds: Seeds

class BackendOverrides(TypedDict):
    """ADVANCED. Raw fragments merged into the compiled input of one environment type (engine YAML keys for uml/dce, program option names for ns3). Anything here makes the scenario environment-specific; the UI should show it as such and hide it by default."""
    
    uml: dict[str, Any]
    
    dce: dict[str, Any]
    
    ms3: dict[str, Any]
    
    rpi4: dict[str, Any]
    
    model: dict[str, Any]

type PathId = str
"""Path identifier, used by events, generators and in the metrics (path_id). 'bottleneck' is reserved."""

type Bandwidth = float
"""Link rate in bit/s (20 Mbit/s = 20000000)."""

type Delay = float
"""ONE-WAY delay added on the link, in seconds (20 ms = 0.02). The round-trip time is about twice the sum over the path, plus queueing."""

type Queue = int
"""Length of the bottleneck queue (drop-tail) in packets. Strongly affects delay and loss; a typical value is 100."""

type Probability = float
"""Probability as a fraction (0.01 = 1 %)."""

type AppliesTo = Literal["data", "all"]
"""data = only data packets in the sender->receiver direction are dropped; all = every packet in both directions (ACKs too). Use 'all' with probability 1 for a silent path failure."""

type Loss = NoLoss|Random|Burst|LossExplicit

class NoLoss(TypedDict):
    
    model: Literal["none"]
    
    applies_to: Optional[AppliesTo]

class Random(TypedDict):
    """Each eligible packet is dropped independently with the given probability."""
    
    model: Literal["bernoulli"]
    
    probability: Probability
    
    applies_to: Optional[AppliesTo]

class Burst(TypedDict):
    """Two-state Markov chain evaluated per packet. Mean burst length = 1/p_bg packets; share of time in the bad state = p_gb/(p_gb+p_bg); mean loss = (p_bg*loss_good + p_gb*loss_bad)/(p_gb+p_bg)."""
    
    model: Literal["gilbert-elliott"]
    
    p_gb: Probability
    """Per-packet probability good -> bad."""
    
    p_bg: Probability
    """Per-packet probability bad -> good (> 0)."""
    
    loss_good: Probability
    """Loss probability in the good state (usually 0)."""
    
    lostt_bad: Probability
    """Loss probability in the bad state (usually 1)."""
    
    applies_to: Optional[AppliesTo]

class LossExplicit(TypedDict):
    """ADVANCED. Drop exactly the eligible packets with these 0-based indices (single-loss tests). UML only."""
    
    model: Literal["list"]
    
    indices: list[int]
    
    applies_to: AppliesTo

class Path(TypedDict):
    
    id: Id
    
    label: str
    """Display name, e.g. 'Wi-Fi' or 'LTE'."""
    
    bandwidth_bps: Bandwidth
    
    delay_s: Delay
    
    queue_pkts: Queue
    
    loss: Loss

class Topology(TypedDict):
    
    mode: Literal["disjoint", "shared"]
    """disjoint = each path has its own bottleneck (independent links); shared = both paths meet in one common bottleneck after their access links (tests fairness to other traffic)."""
    
    bottleneck: Optional[Bottleneck]
    
    cross_traffic: Optional[CrossTraffic]

class Bottleneck(TypedDict):
    """The common bottleneck (shared mode only)."""
    
    bandwidth_bps: Bandwidth
    
    delay_s: Delay
    
    queue_pkts: Queue

class CrossTraffic(TypedDict):
    """Competing single-path TCP flows through the shared bottleneck. Either a fixed schedule or a random on/off generator (or both)."""
    
    cc: Literal["cubic", "reno"]
    """Congestion control of the competing flows."""
    
    delay_s: Delay
    """One-way delay of the cross-traffic access link."""
    
    schedule: list[ScheduleItem]
    
    generator: CrossTrafficGenerator

class ScheduleItem(TypedDict):
    """Rule S-CROSS: start_s < stop_s <= duration_s."""
    
    start_s: float
    
    stop_s: float
    
    flows: int
    """Number of parallel TCP flows in this interval."""

class CrossTrafficGenerator(TypedDict):
    """Random on/off periods (exponentially distributed), drawn from the seed."""
    
    type: Literal["onoff"]
    
    flows: int
    
    mean_on_s: float
    
    mean_off_s: float
    
    start_s: float

type Target = str
"""Id of a path from 'paths', or 'bottleneck' (shared mode; not for set-loss). Rule S-TARGET."""

type AtS = float
"""Time of the change, seconds after the sender start. Rule S-EVENT-TIME: at_s <= duration_s."""

type Event = EventLoss|EventBandwidth|EventDelay|EventQueueLen

class EventLoss(TypedDict):
    
    at_s: AtS
    
    target: Target
    
    action: Literal["set-loss"]
    
    loss: Loss

class EventBandwidth(TypedDict):
    
    at_s: AtS
    
    target: Target
    
    action: Literal['set-bandwidth']
    
    bandwidth_bps: Bandwidth

class EventDelay(TypedDict):
    """Lowering the delay lets later packets overtake earlier ones (reordering), as on a route change."""
    
    at_s: AtS
    
    target: Target
    
    action: Literal['set-delay']
    
    delay_s: Delay

class EventQueueLen(TypedDict):
    
    at_s: AtS
    
    target: Target
    
    action: Literal['set-queue']
    
    queue_pkts: Queue

type Generator = GeneratorDelay|GeneratorOutages

class GeneratorDelay(TypedDict):
    """Every every_s seconds the one-way delay of the path is re-drawn uniformly from [min_delay_s, max_delay_s]. This is how delay variability ('jitter') is modelled; per-packet jitter is not supported."""
    
    type: Literal["random-delay"]
    
    target: Target
    
    start_s: float
    
    every_s: float
    
    min_delay_s: Delay
    
    max_delay_s: Delay

class GeneratorOutages:
    """Silent failures of the path (all packets lost, both directions) of length duration_s, separated by exponentially distributed gaps with mean mean_interval_s."""
    
    type: Literal["outages"]
    
    target: Target
    
    start_s: float
    
    mean_interval_s: float
    
    duration_s: float

type Traffic = TrafficBulk | TrafficMedia

class TrafficBulk(TypedDict):
    """The sender always has data (limited only by the network, the algorithm and the receiver)."""

    type: Literal["bulk"]

class TrafficMedia(TypedDict):
    """Media stream configuration."""

    type: Literal["media"]

    media: Media

class Media(TypedDict):
    """Configuration of a media stream."""

    mode: Literal["cbr", "vbr"]
    
    source: Literal["live", "stored"]

    rate_Bps: float

    fps: int

    close: Literal["hold", "fin"]

    start_delay_s: float

    pause_s: tuple[float, float]

    reverse: bool

class Receiver(TypedDict):
    """Behaviour of the receiving application and its buffers."""
    
    rcvbuf_bytes: int
    """Fixed receive buffer (SO_RCVBUF); disables autotuning. 0 = autotuning."""
    
    rcvbuf_autotune_max_bytes: int
    """Upper limit of receive-buffer autotuning (Linux tcp_rmem max). Omit to use the platform default (16 MiB). Ignored when rcvbuf_bytes > 0."""
    

type read_scheldue = list[ReadScheldueItem]

class ReadScheldueItem(TypedDict):
    """How fast the receiving application reads, as a piecewise-constant schedule. Each entry holds from from_s until the next entry. Rule S-READ: the first from_s is 0 and from_s strictly increases. Omitted = always unlimited. (This is the 'receiver consumption' of the old dashboard draft.)"""
    
    from_s: float
    """Seconds after the connection is accepted."""
    
    rate_Bps: float|None
    """Read rate in BYTES per second; null = unlimited (read as fast as data arrives); 0 = stop reading."""