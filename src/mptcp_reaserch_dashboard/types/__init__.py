lazy import mptcp_reaserch_dashboard.types.scenario as mptcp_scenario
lazy import typing


type Algorithm = typing.Mapping[str, typing.Any] #TODO
type Environment = typing.Mapping[str, typing.Any] #TODO
type Experiment = typing.Mapping[str, typing.Any] #TODO
type Run = typing.Mapping[str, typing.Any] #TODO
type Scenario = mptcp_scenario.Scenario


type Resource = Algorithm | Environment | Experiment | Run | Scenario