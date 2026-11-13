lazy import mptcp_reaserch_dashboard.types.algorithm
lazy import mptcp_reaserch_dashboard.types.environment
lazy import mptcp_reaserch_dashboard.types.experiment
lazy import mptcp_reaserch_dashboard.types.run
lazy import mptcp_reaserch_dashboard.types.scenario



type Algorithm   = mptcp_reaserch_dashboard.types.  algorithm.Algorithm
type Environment = mptcp_reaserch_dashboard.types.environment.Environment
type Experiment  = mptcp_reaserch_dashboard.types. experiment.Experiment
type Run         = mptcp_reaserch_dashboard.types.        run.Run
type Scenario    = mptcp_reaserch_dashboard.types.   scenario.Scenario


type Resource = Algorithm | Environment | Experiment | Run | Scenario