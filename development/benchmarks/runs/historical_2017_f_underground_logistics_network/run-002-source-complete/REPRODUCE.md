# Reproduction

All commands below run from this run directory. Do not write into run-001,
source-recovery or Skill. Raw input is metadata-only in Git: retain/download
the exact original package URL in source-manifest.json and verify every member
hash before placing it under ignored work/source. Never substitute paper data.

environment.json records the actual Python and package versions. Source XLS
uses xlrd and python-calamine; numerical work uses numpy, scipy and networkx.
The run-local optional dependency path is work/deps.

Core numerical stages, after verified inputs/CSV audit:

```powershell
python -X utf8 -B code/run_design.py
python -X utf8 -B code/independent_audit.py
python -X utf8 -B code/scenarios_and_phasing.py
python -X utf8 -B code/operational_simulation.py
python -X utf8 -B code/audit_operations_and_phasing.py
python -X utf8 -B code/plot_results.py
```

run_design overwrites current-run result versions and marks the experiment
RUNNING; do not run it against an already frozen archive unless expressly
creating an authorized new result version. Finalization updates source-bound
evidence and hashes; it does not manufacture experimental outcomes.
Initial infeasibility diagnostics are separately preserved.

Required regression commands and stdout are recorded in validation-results.
The isolated copy uses byte-identical tracked sources solely for required
regressions, with all generated files confined to this run's ignored work.
Its one remaining enclosing-path assertion failure is retained.

The independent static checker deliberately does not import network_model.
The independent train/phase checker deliberately does not import either
simulator or phasing helpers. Compressed commodity and train-leg records are
necessary reconstruction components, not disposable solver iteration traces.
