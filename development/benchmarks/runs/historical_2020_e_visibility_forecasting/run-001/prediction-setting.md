# Prediction setting contract

## Formal Q4 target

| Field | Contract |
|---|---|
| target_variable | Future highway MOR in metres and its strengthening/weakening trend |
| forecast_origin | Last highway frame available when a forecast is issued |
| target_time | Origin plus forecast horizon |
| requested horizon | Not fixed by the statement; includes time until a specified MOR such as 150 m |
| sampling_frequency | Supplied frames are about 41.67 seconds apart |
| history_window | Frames at or before origin only |
| known_at_origin_features | Pixels and derived features from frames at or before origin; future timestamps |
| unknown_future_features | Future frames, realized future weather, future MOR |
| forecast_strategy | Direct horizon-specific mapping for the diagnostic proxy experiment |
| validation_unit | Forecast origin × horizon within the single scene |
| allowed_claim | Relative proxy trend/short-horizon behavior only; not absolute MOR or 150 m dispersal time |
| status | PARTIAL because absolute target labels/calibration are absent |

## Labelled surrogate protocol check

The AMOS series is used only to exercise a labelled future-forecast protocol, not to substitute airport data for Q4.

| Field | Contract |
|---|---|
| target_variable | `MOR_1A(t+h)` metres |
| forecast_origin | Minute `t` in held-out event AMOS20200313 |
| target_time | `t+5`, `t+15`, `t+30` minutes |
| sampling_frequency | 1-minute grid after within-minute aggregation |
| history_window | Lag/rolling windows ending at `t`, maximum 30 minutes |
| known_at_origin_features | MOR history through `t`; meteorological observations at `t` |
| unknown_future_features | Realized weather and MOR after `t` |
| forecast_strategy | DIRECT; an independent target shift/model per horizon |
| validation_unit | Common 30-minute-spaced origins in the later event |
| allowed_claim | Methodological rolling-origin evidence on two supplied airport episodes only |

Every prediction output records origin, target time/frame, horizon, truth, prediction, method, and a provenance field demonstrating that fitted labels/features do not pass the origin.
