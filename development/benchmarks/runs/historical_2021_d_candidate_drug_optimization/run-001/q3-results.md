# Q3 Results

## Class distributions

| Endpoint | Class 0 | Class 1 | Positive prevalence | Majority | Majority prevalence |
| --- | --- | --- | --- | --- | --- |
| Caco-2 | 1215 | 759 | 0.384 | 0 | 0.616 |
| CYP3A4 | 513 | 1461 | 0.740 | 1 | 0.740 |
| hERG | 875 | 1099 | 0.557 | 1 | 0.557 |
| HOB | 1465 | 509 | 0.258 | 0 | 0.742 |
| MN | 460 | 1514 | 0.767 | 1 | 0.767 |

## Selected held-out results

| Endpoint | Model | Threshold | Majority PR-AUC | PR-AUC | ROC-AUC | Balanced Acc. | Recall | Precision | F1 | Specificity | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Caco-2 | logistic | 0.470 | 0.384 | 0.892 | 0.935 | 0.864 | 0.881 | 0.783 | 0.829 | 0.846 | 0.100 |
| CYP3A4 | logistic | 0.400 | 0.740 | 0.984 | 0.959 | 0.907 | 0.876 | 0.976 | 0.923 | 0.938 | 0.073 |
| hERG | extra_trees | 0.510 | 0.557 | 0.958 | 0.951 | 0.876 | 0.882 | 0.895 | 0.888 | 0.870 | 0.086 |
| HOB | extra_trees | 0.220 | 0.258 | 0.801 | 0.920 | 0.854 | 0.886 | 0.635 | 0.739 | 0.823 | 0.096 |
| MN | extra_trees | 0.670 | 0.767 | 0.991 | 0.975 | 0.908 | 0.926 | 0.965 | 0.945 | 0.889 | 0.050 |

All selected models have positive-class recall above zero and Balanced Accuracy well above the 0.5 majority baseline. Full fold dispersion, calibration error, confusion counts, parameters, features, and test probabilities/classes are retained in `outputs/q3-results.json`, `q3-fold-metrics.csv`, and `q3-test-predictions.csv`.
