# Trajectory Fixture Schema

Each YAML file is one control-plane trajectory. Required top-level fields are:

```yaml
id: unique_id
name: readable title
kind: synthetic # or historical
source: path, URL, or source metadata record
source_status: MISSING # ACCEPTED / VERIFIED / MISSING / UNVERIFIED
problem_family: prediction_time_series | optimization_decision | evaluation_simulation_mechanism | classification_prediction_optimization
initial_state: {}
turns: []
```

Each turn contains `turn`, `user`, `expected_trigger`, `expected_route`, and
`expected_phase`. Optional `state_updates` are declarative updates to the
lightweight benchmark state. `p0_risks_add` and `p0_risks_resolve` manage the
blocking-risk list; `assertions.no_fake_experiment` requires explicit
`observed_evidence` before an experiment can be marked complete.

The runner rejects missing required fields. It does not infer experiment
metrics, official facts, or assistant responses from a fixture.

For `kind: historical`, `ACCEPTED` means a user-provided local artifact package
has passed the source gate: `source.yaml` exists, declares
`artifact_origin: USER_PROVIDED`, does not claim `OFFICIAL_DIRECT`, and every
registered raw file exists with a matching SHA256. `VERIFIED` is reserved for
independently verified official provenance. Both statuses count toward
historical Layer A coverage, but they remain distinct in metadata and reports.
