# Backtest protocol

## Airport

- Training begins with the complete earlier AMOS20191216 event.
- AMOS20200313 is a contiguous later holdout/event-transfer period.
- Within the held-out event, origins start after two hours and occur every 30 minutes; the last origin leaves room for the 30-minute target.
- All horizons use the same 43 origins. For each origin/horizon, the expanding fitting set includes rows whose label time is at or before that origin.
- Model/scaler fitting is repeated inside every origin. No final-holdout score selects a model or hyperparameter.
- Fixed horizons: 5, 15, 30 minutes. Metrics are reported separately.

## Highway proxy

- Origins are frames 36, 38, …, 94, yielding 30 common origins for 1/3/6-frame horizons.
- At each origin the expanding fitting set includes only examples whose target frame is already observed.
- Direct Ridge and persistence use identical rows and metrics.
- Because all frames belong to one short episode, this is rolling-origin internal evidence, not an independent-scene final test.

## Intervals

For each method/horizon, no interval is produced until ten earlier out-of-origin absolute errors exist. Later prediction radius is a finite-sample-adjusted 80th percentile of only those prior errors. Coverage and width are measured on subsequent origins.

## Isolation statement

The airport point-forecast holdout is isolated from model choice (`YES`). The highway proxy has no independent final episode (`NO` for independent-scene validation). Neither training residuals nor random splits are reported as forecast evidence.
