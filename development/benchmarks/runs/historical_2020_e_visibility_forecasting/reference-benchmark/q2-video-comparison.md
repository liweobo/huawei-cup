# Q2 airport-video comparison

| ID | Airport video used | Target | Alignment evidence | Split / metric | Assessment |
|---|---|---|---|---|---|
| Frozen | unavailable | intended AMOS MOR | cannot execute without local media | none | SOURCE_BLOCKED |
| R1 | YES | MOR regression | watermark drift/gap and 15s sampling discussed; UTC/tolerance incomplete | stratified random 70/30; R²/RMSE/MAE | TEMPORAL_ALIGNMENT_UNVERIFIED |
| R2 | YES | main-text MOR bands; appendix RVR_1A thresholds | exact LOCALDATE matching attempted, but 37.5–52.5s maps to 30 and target semantics conflict | shuffled train/validation; separate test selection undocumented | MOR_RVR_TARGET_INCONSISTENCY |
| R3 | YES | 0.8 RVR + 0.2 MOR, nine classes | one-minute Beijing records; UTC/drift/tolerance incomplete | split order UNKNOWN; augmentation grouping unclear | author-defined target, not MOR |
| R4 | YES | MOR regression | one-minute frames/records; UTC/drift/tolerance incomplete | same 434 rows used for feature selection, training and testing | TRAIN_FIT_ONLY |
| R5 | YES | six visibility bands; field unspecified | one-minute clips + four-record average; clock rule incomplete | 60/20/20, ordering/grouping UNKNOWN; 17.23% error | TARGET_FIELD_UNSPECIFIED |
| R6 | YES | 22 classes; field/bands unspecified | every 15s by watermark; missing interval recognized; UTC/tolerance incomplete | RANDOM_SPLIT 70/30; 79.63% test accuracy | same-time estimation only |

All six papers demonstrate access to an airport video or equivalent material, but none independently proves that the currently listed remote object is byte-equivalent to the original competition attachment. No paper provides the complete frame timestamp → LOCALDATE → UTC CREATEDATE → match window/tolerance contract requested by this benchmark. Their image results cannot be imported into the frozen run.
