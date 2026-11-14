from enum import Enum, auto
import itertools
import pymongo

lazy import typing
lazy import pymongo.database
lazy import pymongo.collection
lazy import mptcp_reaserch_dashboard.types as mptcp_types


class InvalidResourceError(Exception):
    ...


class ErrorLevel(Enum):
    
    Error = auto()
    Warning = auto()

ValidErrors = typing.Literal[
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
    
    'X-REF',
    'X-PROFILE',
    'X-ALG-DUP',
    'X-SWEEP',
    'W-PROFILE',
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
    
    'X-REF':          (ErrorLevel.Error,   'scenario (id+version), environment and algorithm ids exist in the catalogue'),
    'X-PROFILE':      (ErrorLevel.Error,   'an algorithm with profiles needs an existing profile; one without profiles takes none'),
    'X-ALG-DUP':      (ErrorLevel.Error,   'the same (algorithm, profile) at most once'),
    'X-SWEEP':        (ErrorLevel.Error,   'every sweep path exists; every variant passes the schema and the S-rules'),
    'W-PROFILE':      (ErrorLevel.Warning, 'the chosen profile is not frozen'),
}







def s_path_id(data: mptcp_types.Scenario) -> bool:
    all_unique_paths = {i['id'] for i in data['paths'] if i['id'] != 'bottleneck'}
    return len(all_unique_paths) != len(data['paths'])


def s_target(data: mptcp_types.Scenario) -> bool:
    if data['events'] is not None and data['generators'] is not None:
        
        all_paths = [i['id'] for i in data['paths'] if (i['id'] != 'bottleneck' or data['topology']['mode'] == 'shared')]
        has_bottleneck = 'bottleneck' in all_paths
        
        for i in itertools.chain(data['events'], data['generators']):
            path_exists = i['target'] in all_paths
            is_not_allowed_bottleneck = has_bottleneck and i.get('action') is not None and i.get('action') == 'set-loss'
            
            if not path_exists or is_not_allowed_bottleneck:
                return True
    return False


def s_event_time(data: mptcp_types.Scenario) -> bool:
    if data['events'] is not None:
        for event in data['events']:
            if event['at_s'] > data['duration_s']:
                return True
    return False


def s_event_dup(data: mptcp_types.Scenario) -> bool:
    if data['events'] is not None:
        for iid, event1 in enumerate(data['events']):
            event1 = (event1['at_s'], event1['target'], event1['action'])
            for event2 in data['events'][iid + 1:]: # O(n^2) goes brr
                event2 = (event2['at_s'], event2['target'], event2['action'])
                
                if event1 == event2:
                    return True
    return False


def s_window(data: mptcp_types.Scenario) -> bool:
    if data['statistics_window_s'] is not None:
        start, end = data['statistics_window_s']
        if not (0 <= start < end <= data['duration_s']):
            return True
    return False


def s_gen(data: mptcp_types.Scenario) -> bool:
    generators = data.get('generators')
    if generators is not None:
        for gen in generators:
            if gen['type'] == 'random-delay':
                if not (gen['start_s'] < data['duration_s'] and gen['min_delay_s'] <= gen['max_delay_s']):
                    return True
                    
            elif gen['type'] == 'outages':
                if not (gen['duration_s'] < data['duration_s']):
                    return True
    return False


def s_read(data: mptcp_types.Scenario) -> bool:
    receiver = data.get('receiver')
    if receiver is None:
        return False
    read_schedule = receiver.get('read_schedule')
    if read_schedule is None:
        return False
    
    scheldues = [i['from_s'] for i in read_schedule]
    if scheldues[0] != 0 or scheldues != sorted(scheldues):
        return True
    return False


def s_cross(data: mptcp_types.Scenario) -> bool:
    cross = data['topology'].get('cross_traffic')
    if cross is not None:
        for i in cross['schedule']:
            if not (i['start_s'] < i['stop_s'] <= data['duration_s']):
                return True
    return False


def s_pause(data: mptcp_types.Scenario) -> bool:
    traffic = data['traffic']
    if traffic['type'] == 'media':
        
        pause_s = traffic['media'].get('pause_s')
        if pause_s is None:
            return False
        
        start, stop = pause_s

        if not (start < stop <= data['duration_s']):
            return True
    return False


def s_seeds(data: mptcp_types.Scenario) -> bool:
    defaults = data['defaults']
    if defaults['seeds']['strategy'] == 'explicit':
        if len(defaults['seeds']['values']) != defaults['repetitions']:
            return True
    return False


def w_warmup(data: mptcp_types.Scenario) -> bool:
    statistics_window = data.get('statistics_window_s')
    if statistics_window is not None and data['traffic']['type'] == 'bulk' and statistics_window[0] == 0:
        return True
    return False


def w_delay_twice(data: mptcp_types.Scenario) -> bool:
    ... # ???


def w_bottleneck(data: mptcp_types.Scenario) -> bool:
    topology = data['topology']
    bottleneck = topology.get('bottleneck')
    if topology['mode'] == 'shared' and bottleneck is not None:
        paths_bandwidth = sum(path['bandwidth_bps'] for path in data['paths'])
        if bottleneck['bandwidth_bps'] >= paths_bandwidth:
            return True
    return False


def w_queue(data: mptcp_types.Scenario) -> bool:
    for path in data['paths']:
        if path['queue_pkts'] < 10:
            return True
    return False


def x_ref(data: mptcp_types.Experiment, db: pymongo.database.Database[typing.Any]) -> bool:
    algorithms: pymongo.collection.Collection[mptcp_types.Algorithm] = db['algorithms']
    environments: pymongo.collection.Collection[mptcp_types.Environment] = db['environments']
    scenarios: pymongo.collection.Collection[mptcp_types.Scenario] = db['scenarios']
    
    scenario_id_version = ((i['id'], i['version']) for i in data['scenarios'])
    env_id = data['environments']
    algo_id = (i['id'] for i in data['algorithms'])
    
    for id, version in scenario_id_version:
        if scenarios.find_one({'id': id, 'version': version}) is None:
            return True
    
    for id in env_id:
        if environments.find_one({'id': id}) is None:
            return True
    
    for id in algo_id:
        if algorithms.find_one({'id': id}) is None:
            return True
    
    return False


def x_profile(data: mptcp_types.Experiment, db: pymongo.database.Database[typing.Any]) -> bool:
    algorithms: pymongo.collection.Collection[mptcp_types.Algorithm] = db['algorithms']
    
    for algo in data['algorithms']:
        algo_found = algorithms.find_one({'id': algo['id']})
        
        if algo_found is not None and algo_found['profiles'] is not None:
            if algo['profile'] is None or algo['profile'] not in algo_found['profiles']:
                return True
        else:
            if algo['profile'] is not None:
                return True
        
    return False


def x_alg_dup(data: mptcp_types.Experiment) -> bool:
    
    unique_algos = {(alg['id'], alg['profile']) for alg in data['algorithms']}
    return len(unique_algos) != len(data['algorithms'])


def x_sweep(data: mptcp_types.Experiment) -> bool:
    ... # ???


def w_profile(data: mptcp_types.Experiment, db: pymongo.database.Database[typing.Any]) -> bool:
    algorithms: pymongo.collection.Collection[mptcp_types.Algorithm] = db['algorithms']
    
    for algo in data['algorithms']:
        if algo['profile'] is not None:
            alg_found = algorithms.find_one({'id': algo['id']})
            if alg_found is not None and alg_found['profiles'] is not None:
                
                for profile in alg_found['profiles']:
                    if algo['profile'] == profile['id'] and profile['status'] != 'frozen':
                        return True
    return False
