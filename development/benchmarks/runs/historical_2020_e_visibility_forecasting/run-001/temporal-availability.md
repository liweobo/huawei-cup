# Temporal availability audit

| Data/feature | Available at forecast origin? | Rule |
|---|---|---|
| Current and lagged MOR through origin | yes in AMOS diagnostic | lag timestamp ≤ origin |
| Rolling MOR features | yes | right-aligned window ending at origin; no centered window |
| Current observed airport meteorology | yes | same origin minute only |
| Realized meteorology at `t+h` | no | `UNKNOWN_AT_ORIGIN`; never used |
| Highway pixels through origin frame | yes | frame number ≤ origin frame |
| Future highway frame/pixel | no | target only |
| Calendar/target timestamp | yes | deterministic from origin and horizon |

The AMOS supervised table sets `target_time = feature_time + h`; at every origin the fitting subset satisfies `train_max_target_time <= origin`. Each scaler is fit inside that origin’s training subset. Highway fitting similarly enforces `train_max_target_frame <= origin_frame`. Aggregation occurs within each original minute/event before splitting, never across an origin boundary. No missing-value imputer, backward fill, interpolation, global decomposition, or random split is used.

Synthetic fail-closed probes in `outputs/synthetic_guard_results.json` cover:

- target or realized future weather after origin;
- a rolling window extending after origin;
- random-shuffle forecast evidence;
- recursive `h=2` using observed `y(t+1)`;
- a scaler fitted on post-origin rows;
- time reversal without redefining the forecast origin;
- conversion of the relative image proxy into MOR = 150 m.

All prohibited cases are blocked. The only accepted synthetic case uses current/lagged inputs whose maximum timestamp equals the origin.
