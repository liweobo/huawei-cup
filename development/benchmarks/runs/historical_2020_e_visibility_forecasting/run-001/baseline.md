# Baselines

## Q1 same-time estimation

Baseline: median visibility learned from the other complete event. On held-out AMOS20191216 it achieved MAE 2,713 m and RMSE 2,901 m; on held-out AMOS20200313, MAE 3,340 m and RMSE 3,760 m. This is deliberately simple and exposes the difficulty of cross-event generalization.

## Labelled AMOS future forecast

Persistence uses `y_hat(t+h)=MOR(t)` on exactly the same 43 origins per horizon as direct Ridge.

| Horizon | n | MAE (m) | RMSE (m) | Bias (m) |
|---:|---:|---:|---:|---:|
| 5 min | 43 | 266.9 | 820.4 | 58.7 |
| 15 min | 43 | 360.5 | 972.0 | 53.5 |
| 30 min | 43 | 410.5 | 997.6 | 98.8 |

Seasonal naive is not used: only two isolated 24-hour fog episodes are present, insufficient evidence for a repeatable daily/weekly period. A seasonal baseline would manufacture continuity between unrelated events.

## Highway relative proxy

Persistence uses the current proxy value on the same 30 origins per horizon as direct Ridge. MAE is `4.66e-5`, `8.34e-5`, and `1.16e-4` at 1/3/6 frames. These numbers are in proxy units, not metres.

Baseline and primary methods share origins, horizons, rows, missing policy, and metrics. The baseline remains the preferred airport point forecaster because the primary model does not beat it.
