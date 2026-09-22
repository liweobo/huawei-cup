# Identifiability comparison

## Required chain

An absolute clearing-time claim requires all of the following:

1. a metric highway distance or paired MOR calibration;
2. a valid optical mapping from image observations to extinction/MOR;
3. a target series with known units and error;
4. an explicit forecast origin and allowed inputs;
5. validation that represents the intended future horizon;
6. a supported threshold and uncertainty statement.

| ID | Metric scale | Optical/scene mapping | Highway label validation | Future validation | Clearing-time status |
|---|---|---|---|---|---|
| Frozen | absent | relative proxy only | absent | proxy protocol tested | absolute time UNIDENTIFIABLE and withheld |
| R1 | assumed 9m separation | paper/code ROI conflict | none | none | UNVERIFIED |
| R2 | assumed 3.5m segment | figure/text/code scale conflicts | none | none | UNVERIFIED |
| R3 | assumed road/camera geometry | C0=1 and dark-channel assumptions | none | none | UNVERIFIED |
| R4 | external 6m divider + selected scene points | C0=1, threshold/transmission assumptions | none | none | UNVERIFIED |
| R5 | external road markings + fixed 10m camera | averaged transmission-to-depth chain unverified | none | short historical only | UNVERIFIED |
| R6 | hard-coded 30m in appendix | calibration prose not implemented as printed | none | none | UNSUPPORTED / UNVERIFIED crossing |

The current Skill's evaluation/output semantics already require absolute/relative output type, unit, threshold provenance, comparator compatibility and allowed claims. The frozen refusal to promote a proxy to metres shows that this control worked. The partial status is caused by source and physical identifiability, not a missing forecasting capability.
