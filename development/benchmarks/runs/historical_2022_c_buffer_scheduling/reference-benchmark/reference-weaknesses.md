# Reference Weaknesses

These are observations about evidence quality, not claims that a paper's
reported schedule is necessarily wrong.

| reference | weakness | evidence status |
|---|---|---|
| R-01 | reports heuristic GA results and calls them optimal-ish; no exact bound or independent constraint replay | no optimality proof in text |
| R-02 | claims local optimum/feasible space; no independent workbook replay or solver bound | local/heuristic scope |
| R-03 | reports dynamic-programming model but the implementation is an iterative metaheuristic and does not prove global optimality | heuristic evidence |
| R-04 | reports comparisons and return counts, but the supplied text does not establish independent audit of every output | validation scope |
| R-05 | Q1 GA and Q2 Markov results; no exact bound or independent machine-state replay in supplied text | heuristic evidence |
| R-06 | improved GA result; no global-optimum proof or independent result replay | heuristic evidence |
| R-07 | PDF text layer is degraded; method and result claims cannot all be verified from the extracted text | low-confidence text |

## Important Caveat

No reference is used as a ground-truth answer. They are a reference set
for modeling ideas and a source of evidence about what search structures
were used. Their objective comparisons are treated cautiously because
interpretations, timings, and implementation details may differ.
