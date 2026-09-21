# Numerical Comparability

Direct ranking requires the same node meaning, service scope, corridor
approximation, physical-cost counting, daily conversion, freight coverage and
operational boundary. No reference meets all seven conditions against run-002.

| Quantity | Frozen run-002 | Reference evidence | Decision |
|---|---|---|---|
| Q1 station counts |118primary+118secondary |8+22;4+25;4selected from28;5+27/24 conflict;4+23;4+24;4+23 |Descriptive counts only; NOT_DIRECTLY_COMPARABLE as optimal/feasible alternatives |
| Q2 physical length |8692.161736672km,1120tunnels |Different station sets and links; FK0263 components total119.44km/30tunnels |NOT_DIRECTLY_COMPARABLE; cannot label length reduction a same-service improvement |
| Q2 daily cost |93,223,150.212486yuan, conditional |2.7833million;4.07million;2.4813million/day claims in selected papers; others different/unclear basis |NOT_DIRECTLY_COMPARABLE, no ratio or winner reported |
| Q3 distance/time |Real timed policies leave27.478101/143.521733t |Selected path~25% improvement in F90005027;15%/35% availability/accessibility in F10710008 |Different outcomes/OD/failure scopes; NOT_DIRECTLY_COMPARABLE |
| Q4 saturation year |2, retained routing, source year0 |F90005027 narrative18/table17;FK0263 reserve model4; others differing criteria |NOT_DIRECTLY_COMPARABLE; index, tracks, dispatch and criterion differ |

## Per-Paper Blocking Differences

| Reference | Why its result cannot establish numerical dominance |
|---|---|
| F10256001 |Partial area coverage, symmetric-return assumption, ground-capacity contradictions, annual/daily boundary |
| F10294003 |Changed OD/service, secondary overload,360-day depreciation, nominal per-track capacity |
| F10486024 |Role/site count ambiguity, fixed-ring scope,10t interprimary table conflict, annuity accounting |
| F10703002 |Conflicting counts, unclear cost time basis, uncalibrated capacity, incomplete aggregation |
| F10710008 |Intrazonal exclusion, symmetric aggregate ambiguity, component accounting, probability metric defects |
| F90005027 |Row-origin mismatch, congestion spatial averaging, ground-bound inconsistency, different saturation basis |
| FK0263 |Congestion-only underground quota, balanced park service/common fractions, nominal line capacity, omitted residual surface cost |

The clear qualitative signal is **MODEL_SCOPE_LIMIT / ALGORITHM_QUALITY_LIMIT**:
run-002 explored a very restrictive and expensive construction. It is reasonable
to expect broader legal hierarchy/search to matter, but this stage provides no
same-protocol numerical lower bound or improved feasible design. Published
numbers are retained as reported, with units and provenance, not corrected
into fabricated new solutions.
