# Horizon-specific metrics

## Airport MOR forecast (metres)

All rows use 43 common origins in held-out AMOS20200313.

| Horizon | Method | MAE | RMSE | Median AE | Bias | Spearman |
|---:|---|---:|---:|---:|---:|---:|
| 5 min | persistence | 266.9 | 820.4 | 50.0 | 58.7 | 0.985 |
| 5 min | direct Ridge | 972.3 | 1535.7 | 344.5 | −384.2 | 0.934 |
| 15 min | persistence | 360.5 | 972.0 | 50.0 | 53.5 | 0.979 |
| 15 min | direct Ridge | 1103.7 | 1718.5 | 523.8 | −455.2 | 0.924 |
| 30 min | persistence | 410.5 | 997.6 | 50.0 | 98.8 | 0.963 |
| 30 min | direct Ridge | 1049.7 | 1706.8 | 453.1 | −481.7 | 0.925 |

Relative to persistence, direct Ridge has 264%, 206%, and 156% larger MAE at 5/15/30 minutes. The primary candidate fails to earn preference; persistence is the selected point-forecast baseline. Direction accuracy for persistence is structurally zero on non-ties because it forecasts no change, illustrating that level-error and change-direction goals are different. Ridge direction accuracy is 0.41/0.50/0.57, not strong evidence.

Low-visibility subset uses the problem-given 150 m example. At 5/15/30 minutes there are 12/12/14 evaluated targets. Persistence MAE is 12.5/4.2/92.9 m; Ridge MAE is 42.2/75.2/112.3 m. The instrument’s floor/special values make these figures coarse and they are not independent-event counts.

## Highway relative contrast proxy

All rows use 30 common origins; units are dimensionless proxy units.

| Horizon | Method | MAE | RMSE | Direction accuracy |
|---:|---|---:|---:|---:|
| 1 frame (0.69 min) | persistence | 4.664e-5 | 5.698e-5 | 0.00 |
| 1 frame | direct Ridge | 4.530e-5 | 6.319e-5 | 0.60 |
| 3 frames (2.08 min) | persistence | 8.341e-5 | 1.111e-4 | 0.00 |
| 3 frames | direct Ridge | 8.883e-5 | 1.155e-4 | 0.57 |
| 6 frames (4.17 min) | persistence | 1.164e-4 | 1.490e-4 | 0.00 |
| 6 frames | direct Ridge | 1.003e-4 | 1.304e-4 | 0.80 |

Ridge’s mixed advantage on one very short episode does not validate absolute visibility. The full-episode robust slope indicates improving contrast, while short-horizon changes remain noisy.
