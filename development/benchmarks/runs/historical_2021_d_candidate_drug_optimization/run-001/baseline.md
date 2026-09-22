# Baselines

| Baseline | Primary metric | Secondary metric | Role |
| --- | --- | --- | --- |
| Q2 mean | 1.423 | 1.190 | location baseline |
| Q2 median | 1.423 | 1.190 | robust location baseline |

Q3 majority baselines have Balanced Accuracy 0.5 for every endpoint and PR-AUC equal to prevalence. Their full values appear beside selected models in `q3-results.md`. Q4 first establishes the observed training baselines recorded in `q4-results.json`, including a direction-robust baseline, before any test-candidate rank is considered.
