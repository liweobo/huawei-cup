# Q4 Results

| Scenario | Candidate | Pred. pIC50 | Pred. IC50 nM | Activity SD | Primary favorable | Alternate favorable | Domain | Objective |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Primary assumption | TEST026 | 6.414 | 385.763 | 0.115 | 3 | 2 | PASS | 6.298 |
| CYP3A4 reversed | TEST019 | 7.139 | 72.614 | 0.146 | 2 | 3 | PASS | 6.993 |

Under the primary assumption, 1 of 50 candidates pass every gate and `TEST026` is the finite-domain surrogate best. Reversing the unresolved CYP3A4 direction leaves one candidate but changes it to `TEST019`. The ranking is therefore **conditional**, and no single compound is recommended without deciding the CYP3A4 criterion.

The best observed direction-robust training baseline is `TRAIN1423` with observed pIC50 8.772, IC50 1.691 nM, and favorable counts 4/3 under the two directions. Predicted test values are not claimed to beat this observed baseline. Empirical descriptor ranges in `q4-descriptor-profiles.csv` summarize the 160 top-quartile, primary-gate training compounds and remain association ranges rather than edit instructions.
