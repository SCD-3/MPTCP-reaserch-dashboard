from enum import Enum, auto
from typing import Literal

class ErrorLevel(Enum):
    
    Error = auto()
    Warning = auto()

ValidErrors = Literal[
    'S-PATH-ID',
    'S-TARGET',
    'S-EVENT-TIME',
    'S-EVENT-DUP',
    'S-WINDOW',
    'S-GEN',
    'S-READ',
    'S-CROSS',
    'S-PAUSE',
    'S-SEEDS',
    
    'W-WARMUP',
    'W-DELAY-TWICE',
    'W-BOTTLENECK',
    'W-QUEUE',
    
    'E-PATHS',
    'E-TOPOLOGY',
    'E-CROSS',
    'E-TRAFFIC',
    'E-EVENT',
    'E-GENERATOR',
    'E-LOSS',
    'E-READ',
    'E-QUEUE',
]

errors: dict[ValidErrors, tuple[ErrorLevel, str]] = {
    
    'S-PATH-ID':      (ErrorLevel.Error,   'path ids are unique; `bottleneck` is not a path id'),
    'S-TARGET':       (ErrorLevel.Error,   'every `events[].target` / `generators[].target` is an existing path id, or `bottleneck` only in shared mode and not for `set-loss`; generators target paths only'),
    'S-EVENT-TIME':   (ErrorLevel.Error,   '`events[].at_s <= duration_s`'),
    'S-EVENT-DUP':    (ErrorLevel.Error,   'no two events with the same (`at_s`, `target`, `action`)'),
    'S-WINDOW':       (ErrorLevel.Error,   '`0 <= statistics_window_s[0] < statistics_window_s[1] <= duration_s`'),
    'S-GEN':          (ErrorLevel.Error,   'generator `start_s < duration_s`; `min_delay_s <= max_delay_s`; outage `duration_s < duration_s` of the run'),
    'S-READ':         (ErrorLevel.Error,   '`read_schedule` starts at `from_s = 0`, `from_s` strictly increasing, none after the end'),
    'S-CROSS':        (ErrorLevel.Error,   'cross-traffic schedule: `start_s < stop_s <= duration_s`'),
    'S-PAUSE':        (ErrorLevel.Error,   'media `pause_s`: `from < to <= duration_s`'),
    'S-SEEDS':        (ErrorLevel.Error,   'an explicit seed list has exactly `repetitions` values (scenario defaults and experiment overrides)'),

    'W-WARMUP':       (ErrorLevel.Warning, 'bulk traffic with a statistics window starting at 0 (slow start included)'),
    'W-DELAY-TWICE':  (ErrorLevel.Warning, 'a path has both `set-delay` events and a `random-delay` generator'),
    'W-BOTTLENECK':   (ErrorLevel.Warning, 'the shared bottleneck is not slower than all paths together (it never limits)'),
    'W-QUEUE':        (ErrorLevel.Warning, 'a queue shorter than 10 packets'),

    'E-PATHS':        (ErrorLevel.Error,   '`min_paths <= len(paths) <= max_paths`'),
    'E-TOPOLOGY':     (ErrorLevel.Error,   '`topology.mode` in `topology_modes`'),
    'E-CROSS':        (ErrorLevel.Error,   'cross traffic only if `cross_traffic: true`'),
    'E-TRAFFIC':      (ErrorLevel.Error,   '`traffic.type` in `traffic_types`'),
    'E-EVENT':        (ErrorLevel.Error,   'every `events[].action` in `event_actions`'),
    'E-GENERATOR':    (ErrorLevel.Error,   'every generator `type` in `generator_types`'),
    'E-LOSS':         (ErrorLevel.Error,   'every loss model used (paths and `set-loss` events) in `loss_models`; its `applies_to` in `loss_applies_to`'),
    'E-READ':         (ErrorLevel.Error,   'a limited `read_schedule` only if `read_schedule: true`'),
    'E-QUEUE':        (ErrorLevel.Warning, 'a queue above `supported_queue_pkts_max`: allowed, but the run is labelled exploratory'),
}