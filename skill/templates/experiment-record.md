# Experiment Record

This file is a human-readable companion only. Every observed experiment or
validation result requires a structured [`experiment-record.yaml`](experiment-record.yaml)
inside the active run workspace; this Markdown file cannot satisfy the runtime gate.

Experiment ID:
Problem:
Model:
Dataset / Version:
Feature Set:
Parameters:
Random Seed:
planned_protocol:
executed_protocol:
protocol_changed: false
change_reason:
comparable_to_original_plan: true
Split / Validation:
Metrics:
Result (actual run / NOT RUN):
Conclusion:
Keep / Reject:
Reason:
Environment / Command:
Files / Hashes:
artifacts:
status: PLANNED
Failure Notes:
# Include this section only for longitudinal prediction:
temporal_scope:
  target_horizon:
  feature_cutoff:
  post_horizon_records_excluded: 0
  temporal_gate_status: UNVERIFIED
invalidation_reason:
