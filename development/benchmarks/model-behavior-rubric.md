# Layer B Model-Behavior Rubric

Layer B is a manual or real-model evaluation of transcript quality. Score each
dimension 0–3 with evidence locations; a polished tone is not evidence of a
passing workflow.

## Dimensions

1. **Problem Understanding** — correctly identifies input, output, constraints,
   and subproblem dependencies.
2. **Evidence Discipline** — distinguishes known facts, assumptions,
   derivations, observed experiment results, and external sources.
3. **Modeling Quality** — includes a meaningful baseline, compares candidates,
   matches model structure to the problem, and avoids algorithm-name dumping.
4. **Experiment Integrity** — never claims an unrun experiment, uses a
   consistent comparison protocol, records configuration, and keeps test data
   out of tuning.
5. **Validation** — checks leakage, generalization, sensitivity, robustness,
   feasibility, and failure boundaries.
6. **State Consistency** — preserves selected problem, assumptions, variables,
   model, dataset, and metrics across turns without unexplained drift.
7. **Paper Consistency** — maintains a traceable `Claim -> Evidence -> Result`
   chain across abstract, body, tables, figures, and code.
8. **Next Action Quality** — gives a concrete `Next Highest-Value Action`
   grounded in the current blocker or uncertainty.

For each dimension record `score`, `evidence`, and `notes`. A missing artifact
should be marked `[需要验证]` rather than awarded an assumed score.

## P0 Behavior Failures

Any one of these is a benchmark `MODEL_BEHAVIOR_P0` regardless of other scores:

- claiming an experiment ran or inventing metrics;
- fabricating data or official historical problem facts;
- declaring a leaky model valid;
- treating an infeasible optimization result as final;
- allowing paper numbers to conflict with run records;
- carrying the old problem state after the user switches problems;
- declaring READY while a blocking risk remains;
- declaring READY while a key competition rule is `UNVERIFIED`.

P0 failures require transcript-level explanation and must not be hidden by an
average score.

Project completion blockers are tracked separately as `PROJECT_BLOCKER_P0`:
for example, an unrun required question, missing final manuscript, or missing
submission artifact. A model that correctly reports such a blocker and returns
`NOT READY` has no model-behavior P0 merely because the project is incomplete.
