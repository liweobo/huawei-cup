# Forecast strategy

Strategy: `DIRECT`.

For each horizon `h`, a separate supervised target is constructed at the true time/frame offset. Rows are eligible for fitting only when that target was already observable at the forecast origin. Direct models therefore never consume a model-generated intermediate step or the true `y(t+1)` when producing `h>1`.

Airport horizons are 5/15/30 minutes on a verified one-minute grid. Highway horizons are 1/3/6 actual frame offsets, approximately 0.69/2.08/4.17 minutes. Horizon-specific sample availability is retained in prediction tables (`train_rows`) and all evaluated methods use common origins.

Recursive forecasting was not used. The synthetic reviewer probe nevertheless rejects a recursive `h=2` implementation that feeds observed `y(t+1)`, under `RECURSIVE_TARGET_LEAKAGE`.

No future exogenous forecast is supplied by the problem. Realized `t+h` weather is classified `UNKNOWN_AT_ORIGIN` and excluded. Current origin weather is permitted in the labelled airport diagnostic; the highway forecast uses image-derived history only.
