# Reference Consensus

## Set

Total PDFs enumerated: **7**

Fully or substantially reviewed for method structure: **6**

Partially reviewed because of degraded text extraction: **1** (`R-07`)

## Consensus Table

| modeling idea | appears in n papers | total reviewed | supporting references | evidence strength |
|---|---:|---:|---|---|
| target sequence or assignment as candidate | 7 | 7 | R-01 through R-07 | HIGH |
| feasible decoder / simulation / state evaluation | 6 | 7 | R-01, R-03, R-04, R-05, R-06, R-07; R-02 uses constructive guardrails | HIGH |
| constructive greedy or heuristic initial solution | 5 | 7 | R-01, R-02, R-04, R-05, R-07 | MEDIUM-HIGH |
| neighborhood or iterative improvement after construction | 5 | 7 | R-01, R-02, R-03, R-04, R-05/R-06 | HIGH |
| multi-step, population, or iterative search rather than one-step greedy | 6 | 7 | R-01 through R-06 | HIGH |
| sequence/lane/return decisions as search actions | 6 | 7 | R-01 through R-06 | HIGH |
| explicit return-lane decision in the model/search | 6 | 7 | R-01 through R-06 | HIGH |
| staged or layered method (initialization, improvement, Q1/Q2 adaptation) | 6 | 7 | R-01 through R-06 | HIGH |
| objective decomposition or local contribution scoring | 4 | 7 | R-01, R-03, R-04, R-06 | MEDIUM |
| exact solver or proven bound | 0 | 7 | none | HIGH as absence of proof |
| independent final workbook audit | 0 | 7 | none explicitly established | MEDIUM-HIGH |

## What The Consensus Does Not Say

It does **not** say:

- that GA or SA is required;
- that the current state-coupled representation is wrong;
- that a target-sequence representation is inherently invalid;
- that the return lane must always be used;
- that any reference score is directly comparable without rule/timing
  alignment.

It does say that the common solution pattern is constructive feasibility
plus a feasible, structure-aware improvement/search phase that repeatedly
evaluates the real schedule. The current Skill has the first half and a
valid one-step second half, but not the improvement/search phase.
