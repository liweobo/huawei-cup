# Cross-Task Integration Comparison

| solution | Q1 → Q2 | Q3 → Q4 | Q2 → Q4 | integration class | material limitation |
|---|---|---|---|---|---|
| Frozen `run-001` | explicit feature contract | five endpoint predictions, thresholds, hard gates | activity prediction + fold SD | `FULLY_LINKED` | source CYP3A4 ambiguity remains conditional |
| R1 | Q1 20 descriptors reused | common 359-descriptor classifiers feed GA constraint | RF activity feeds GA | `FULLY_LINKED` conceptually | common Q3 set unjustified; no fold-safe handoff |
| R2 | Q1 20 descriptors reused | HGB classifications feed score | HGBRT activity feeds scalarization | `FULLY_LINKED` conceptually | test reuse and arbitrary endpoint/activity weighting |
| R3 | Q1/Q2 features feed activity model | endpoint feature union feeds DE constraints | GBRT activity feeds DE | `FULLY_LINKED` conceptually | continuous-vector feasibility unverified |
| R4 | Q1-derived pool feeds LightGBM | endpoint models feed multiobjective PSO | LightGBM activity feeds PSO | `FULLY_LINKED` conceptually | test-informed selection and pre-split SMOTE |
| R5 | Q1/Q2 features feed XGBoost | endpoint models define reward | activity and reward are described jointly | `PARTIALLY_LINKED` | appendix code appears to optimize the activity and ADMET blocks separately |

Conceptual arrows alone do not guarantee valid integration. The frozen run records row alignment, feature-set contracts, fold provenance, prediction tables, hard/soft separation, candidate IDs, and independent reconstruction across task boundaries. The references generally link model outputs but do not preserve an equivalent auditable evidence chain.

The reference set does not reveal a missing cross-task integration primitive. `CROSS_TASK_INTEGRATION` is rated `STRONG`.
