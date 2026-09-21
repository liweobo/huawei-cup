# Competition State

Status: COMPLETE
Last Updated: 2026-09-21

ACTIVE_RUN_ID: run-001
Workspace Manifest: workspace-manifest.yaml
Allowed Write Root: development/benchmarks/runs/historical_2007_a_food_safety_evaluation/run-001
Prior Run Artifacts Visible: false for modelling evidence; protected history read only for integrity hashes/tests
ACTIVE_EVIDENCE_SET: active-evidence-set.yaml

Selected Problem: 2007A food hygiene safety assurance and risk evaluation
Domain Context: multi-stage dietary exposure and regulatory risk assessment
Current Phase: complete blind run awaiting human review

Q1: overall architecture modelled
Q2: optional intake survey model modelled
Q3: censored contaminant distribution modelled and synthetically run
Q4: risk/compliance/triage modelled and synthetically run
Q5-Q8: censoring, unpaired data, taxonomy, and regional transport addressed conditionally

Data Audit: source extraction VERIFIED; no numeric attachment
Baseline: observed synthetic
Primary Model: observed synthetic, operational claim conditional
Validation: synthetic contracts PASS
Sensitivity: tail high; ranking PARTIAL
Robustness: hard class/top-three stable in declared ranking probes

Paper Status: benchmark report complete
Code Status: complete and tested
References Status: no external data/references used

P0 Risks: frozen Skill lacks mandatory evaluation output-semantics contract
P1 Risks: real inputs absent; extreme-tail/dependence/transport uncertainty

Current Task: EIGHTH HISTORICAL PROBLEM BLIND RUN
Next Highest-Value Action: human review; do not change Skill or start post-hoc comparison automatically
