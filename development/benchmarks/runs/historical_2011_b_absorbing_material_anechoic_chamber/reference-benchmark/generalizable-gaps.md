# Generalizable gap candidates

| candidate | evidence from Blind Run | evidence from references | level | decision |
|---|---|---|---|---|
| `MECHANISM_MODEL_CLOSURE_GATE` | Q1 required added entry coordinate and retained a parametric result | multiple references fix, sample or omit entry position; Q2 papers also use implicit path termination | P1 | TOP 1 |
| `MECHANISM_APPROXIMATION_LADDER_AND_MODEL_DISCREPANCY_GATE` | Blind Run compared a baseline and mechanism model but did not have a reference-family discrepancy test | same rho produces 0.0035-0.0297+ across model families; one paper presents two materially different models | P1 candidate | retain as evidence under TOP 1, not a second gap |
| `TRUNCATION_AND_TAIL_CERTIFICATE` | Blind Run has image-order and time/area refinement plus an upper certificate | many references state finite counts without tail bounds | P1 candidate | useful sub-check of closure gate |
| `PHYSICAL_PARAMETER_IDENTIFIABILITY_GATE` | scalar rho is given but full material response is unavailable | all references use effective rho without independent frequency/phase data | P1/P2 | important limitation, but not the first failure in this run |

## TOP-1 selection

Select `MECHANISM_MODEL_CLOSURE_GATE`. It is domain-neutral, directly caused the first meaningful Blind Run limitation, changes whether a unique numerical answer exists, and is supported by independent variation across the reference set. The approximation ladder and truncation checks should be requirements within the same gate rather than separate Skill repairs.
