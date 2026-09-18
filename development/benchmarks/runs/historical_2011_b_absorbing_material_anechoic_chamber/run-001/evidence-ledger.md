# Evidence ledger

| Artifact ID | Type | Path | Provenance |
|---|---|---|---|
| ART-SOURCE-DOC | SOURCE | `source/2011B题吸波材料与微波暗室问题的数学建模.doc` | SHA256 in `source-provenance/source.json` |
| ART-SOURCE-FACTS | FACTS | `problem-facts.md` | frozen from source extraction; hash in `source-provenance/facts-freeze.json` |
| ART-PARAMETERS | PARAMETERS | `parameters.json` | explicit GIVEN / ASSUMED ledger |
| ART-SIMULATE | CODE_RUN | `code/simulate.py` | executed under Python 3.12.10, NumPy 2.5.2, SciPy 1.18.1 |
| ART-Q1-SCENARIOS | EXPERIMENT_RESULT | `outputs/q1-scenarios.csv` | 144 real deterministic scenarios |
| ART-Q2-CURVES | EXPERIMENT_RESULT | `outputs/q2-time-curves.csv` | 81 time points, K=40, nq=3 |
| ART-CONVERGENCE | VALIDATION_RESULT | `numerical-checks.md`, `outputs/q2-order-convergence.csv`, `outputs/q2-area-convergence.csv` | real refinements |
| ART-PHYSICAL-CHECKS | VALIDATION_RESULT | `physical-sanity-checks.md`, `outputs/physical-checks.json` | analytic/path/limit checks |
| ART-FIGURES | FIGURES | `results/figures/*.png` | generated from CSV outputs by `code/plot_results.py` |
| ART-REVIEW | REVIEW | `review/reviewer-report.md` | evidence-based blind-run review |

Temporary conversion/cache files under `.tmp/` are not evidence and are excluded from the final commit.
