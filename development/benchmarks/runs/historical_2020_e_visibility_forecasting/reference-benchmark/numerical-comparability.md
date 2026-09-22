# Numerical comparability

Direct numerical comparison is allowed only when input/video, label definition, MOR/RVR semantics, scene, timestamp interval, forecast origin, horizon, metric and validation protocol agree.

| Comparison | Result | Blocking mismatches |
|---|---|---|
| Frozen Q1 vs R1–R6 Q1 fit values | NOT_DIRECTLY_COMPARABLE | different targets/transforms, event use, caps and validation; most reference metrics are training fit |
| Frozen missing Q2 vs reference Q2 | NOT_DIRECTLY_COMPARABLE | video absent locally; targets include MOR, RVR, mixtures or unspecified classes; split/alignment differ |
| Frozen highway proxy vs reference Q3 metres | NOT_DIRECTLY_COMPARABLE | relative vs absolute output; paper-only scene scales and no common ground truth |
| Frozen highway 1/3/6-frame errors vs reference Q4 | NOT_DIRECTLY_COMPARABLE | proxy vs paper MOR, much shorter horizons, different origins and no reference future truth |
| Frozen AMOS 5/15/30min metrics vs reference Q4 | NOT_DIRECTLY_COMPARABLE | different location/source/target/scene; AMOS is a protocol diagnostic, not a highway substitute |
| R1–R6 crossing times against each other | NOT_DIRECTLY_COMPARABLE | different Q3 calibrations, time grids, origins, models, thresholds and validation semantics |

The only valid qualitative comparisons concern protocol: whether target time is future, origin is explicit, features are available, validation emulates issuance, a naive comparator is present, horizons are scored separately, and uncertainty is checked. On those dimensions the frozen run is generally stronger.
