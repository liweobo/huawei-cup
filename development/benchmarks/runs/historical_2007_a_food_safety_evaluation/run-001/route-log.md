# Frozen Skill Route Log

| Phase | Frozen route/reference | Application |
|---|---|---|
| Problem analysis | `analyze_problem` | extracted tasks, inputs, outputs, constraints, units, and fact/assumption boundary |
| Model design | `design_model` + `models/evaluation.md` | selected a simple exposure baseline and one materially different censored/hard-gate primary; rejected method zoo |
| Baseline | `build_baseline` | actually ran nondetect-zero empirical tail and equal-weight secondary score |
| Experiment | `run_experiment` | created planned structured record before numeric run and wrote run-scoped outputs |
| Validation | `validate_model` | ran sensitivity, hard constraint, dominance, monotonicity, scale, semantics, and tail checks |
| Review | `reviewer` | reported P0-P2 with evidence, impact, minimal fix, and recheck |

Spectral, temporal-prediction, group-validation, ordinal, imbalanced-classification, stateful scheduling, and mechanism-closure contracts were reviewed through routing but not activated because this task contains none of their activation conditions. Risk-distribution simulation is statistical evaluation, not a physical/dynamic mechanism simulation.
