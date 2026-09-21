# Reviewer Report

Overall solution status: `NEEDS REAL-WORLD EVIDENCE` for operational food-safety claims; `VALID SYNTHETIC BLIND-RUN EVIDENCE` for the declared benchmark.

## P0 Critical

| ID | Evidence location | Issue | Impact | Minimal fix | Recheck |
|---|---|---|---|---|---|
| P0-EVAL-SEMANTICS | Frozen `skill/references/models/evaluation.md`; `problem-facts.md`; `evaluation-target.md` | The frozen Skill has no mandatory pre-weighting contract that distinguishes absolute probability/quantile, regulatory compliance, relative score, rank, and class or requires threshold provenance. 2007A's formal target is `Q_0.99999(D)` versus a hard authority standard, while ranking is not requested. | A generic evaluation route can produce an AHP/TOPSIS/weighted score, allow inappropriate compensation, or report `0.82` as “82% safe,” invalidating the decision. The user-supplied benchmark guards prevented that error in this run; the frozen Skill alone does not guarantee it. | After this blind run is frozen and reviewed, add a lightweight evaluation-target/output-semantics contract and forbid score-to-probability/compliance promotion. Do not add an algorithm or platform. | Run cross-domain synthetic cases: safety threshold, supplier gate, city ranking, education class; require correct output semantics and hard-gate behavior. |

This is the **first meaningful frozen-Skill failure** and the single top generalizable gap. It is not a complaint that a specific MCDM algorithm is absent.

## P1 Serious

| ID | Evidence location | Issue | Impact | Minimal fix | Recheck |
|---|---|---|---|---|---|
| P1-TAIL | `outputs/exposure-results.json`; `sensitivity.md` | The `99.999%` tail remains sensitive to simulation size and contamination-scale uncertainty. | A point estimate can cross a hard threshold incorrectly. | Fit/validate a tail method, use design/bootstrap/model-form uncertainty, and gate on an upper bound. | Coverage study on synthetic families plus real sampling-design audit. |
| P1-DATA | `external-data-ledger.md` | No real survey, monitoring, taxonomy, standard, or body-weight/units data are supplied. | No actual national/regional result is identifiable. | Acquire versioned authoritative inputs and rerun the full chain. | Source/units/time-scope audit. |
| P1-DEPENDENCE | `assumptions.md`; `model.md` | Conditional independence, crosswalk shares, and regional transport are unverified. | Upper-tail exposure may be understated or overstated. | Run dependence, crosswalk, and leave-region-out sensitivity with real support. | Confirm conclusion/class stability. |
| P1-RANK | `sensitivity.md` | Baseline first place changes with weights/indicator deletion; primary top two are near-tied. | A unique “winner” recommendation would be overclaiming. | Recommend by hard class and driver; retain tie/partial stability. | Perturb weights, indicators, and input uncertainty jointly. |

## P2 Important

| ID | Evidence location | Issue | Fix |
|---|---|---|---|
| P2-SOURCE-WORDING | `problem-facts.md` | Source describes a nonnegative decreasing-density contaminant distribution as “left-skewed,” which does not by itself identify skew/family. | Preserve as source wording and test distributional form; already done. |
| P2-BASELINE-OVERLAP | `indicator-ledger.md`; `weighting.md` | Point and upper ratios overlap semantically in the additive baseline. | Keep only as transparent stress baseline; primary is non-additive; already disclosed. |

## P3 Polish

No material P3 issue. Plots could improve presentation, but the retained JSON/Markdown evidence is sufficient and avoids nonessential artifacts.

## Evidence and questions required for operational use

1. Which standard version and unit apply to each contaminant/population/food scope?
2. What are the actual survey/monitoring sampling frames and inclusion probabilities?
3. Are LOD/LOQ and method identifiers available for every nondetect?
4. What crosswalk maps historical/current food taxonomies, and where are mappings ambiguous?
5. What dependence between intake and contamination is supported?
6. Does the tail uncertainty bound have validated coverage near `0.99999`?

## Fix order

- **Must fix before real claim:** standard/data provenance, units/taxonomy, censoring, tail uncertainty, dependence/transport.
- **Should fix after blind-run review:** the single frozen-Skill evaluation semantics gap.
- **May defer:** presentation plots and nonessential alternative methods.

No fix was applied to `skill/` during this run.
