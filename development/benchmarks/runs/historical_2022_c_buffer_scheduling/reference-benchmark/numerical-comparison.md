# Numerical Result Comparison

## Comparability Rule

A numerical score is compared only when the paper states the same task,
the statement weights, and enough timing/rule semantics to align the
objective. Otherwise the entry is `NOT DIRECTLY COMPARABLE`.

| source | Q1 reported | Q2 reported | return use | timing | comparability |
|---|---:|---:|---:|---:|---|
| current run-002 best-found | 53.367 | 53.643 | 0 | 3567 / 3591 s | own frozen run |
| current run-003 state-coupled | 51.801 | 53.058 | Q1 5 actions; Q2 0 | 3934 / 3877 s | state-coupled target; not a score win |
| R-01 | 26.91 | 28.72 | not cleanly extracted as a count | not cleanly extracted | NOT DIRECTLY COMPARABLE |
| R-02 | 15.394 | 26.808 | 22 / 9 | 2640 / 2826-2963 s | NOT DIRECTLY COMPARABLE |
| R-03 | 18.916 / 19.459 variant | 44.469 / 45.78 variant | 6 / 8 or 6 / 4 | 3056 / 2996-3014 s | NOT DIRECTLY COMPARABLE |
| R-04 | 32.086 / 33.646 variant | 63.720 / 64.972 variant | Q2 can be 0 | 3.51%-12.22% reductions | NOT DIRECTLY COMPARABLE |
| R-05 | objective components reported; score extraction incomplete | objective components reported | explicit return-related modeling | 3816 / 3744 s for one run | NOT DIRECTLY COMPARABLE |
| R-06 | 13.67 | 26 | not cleanly extracted | 4022 / 3146 s | NOT DIRECTLY COMPARABLE |
| R-07 | 20.8910 | 43.7220 | extraction degraded | extraction degraded | NOT DIRECTLY COMPARABLE |

## Why The Numbers Cannot Be Ranked

- The papers use different problem interpretations, timing conventions,
  simulator assumptions, and score-handling practices.
- Some papers report objective components that can exceed 100 or become
  negative; the statement does not define all of those extrapolations
  identically.
- Some values are reported for different variants or different iterations
  of the same paper.
- Several papers do not provide the submitted workbook or an independent
  feasibility replay in the extracted text.

## What Is Comparable Qualitatively

The current Skill's **feasibility discipline** is stronger and its
**search quality** is weaker. The reference papers generally explore a
larger structured action space and report nontrivial O1 behavior, while the
current run-002/run-003 candidates do not improve O1. This qualitative
comparison is the basis for the gap diagnosis; the numeric rank is not.
