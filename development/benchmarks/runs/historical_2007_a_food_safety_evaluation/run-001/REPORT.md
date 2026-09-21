# 2007A Eighth-Problem Blind Run

## 1. Source Provenance

Source directory: `https://github.com/zhanwen/MathModel/tree/master/国赛试题/2007年研究生数学建模竞赛试题`

Target file: `2007年A题  建立食品卫生安全保障体系数学模型及改进模型的若干理论问题（终）.doc`

- Git blob supplied and recomputed: `42ab94a3cd6fd90ed59bc13aaa2c0678c4304d44`;
- SHA256: `894369f3e70e648dc552c4b2309f0bb56bcf854f1bf6554c5e38cfa8370b8c4a`;
- bytes: `25,600`;
- source status: `USER_DESIGNATED_HISTORICAL_MIRROR`, not independently verified official origin;
- excellent solutions accessed: `false`.

Legacy extraction is `VERIFIED`: Word 16.0 read-only extraction/export, independent OLE piece-table decoding, and visual inspection of all three pages agree. The document contains zero source tables, equation objects, and images. The original is preserved unchanged.

## 2. Problem Facts

The statement asks for an overall assurance system, an optional population intake model, a contamination-distribution model, a risk model, and detailed analysis of censoring, unpaired samples, incompatible taxonomies, regional-to-national inference, and extreme-quantile precision. It provides no numerical attachment.

The formal risk target is a population distribution of daily contaminant intake and especially its `99.999%` right quantile. Safety is supported only by comparison with an applicable authority standard in compatible units.

## 3. Evaluation Target

The assessment object is a declared population × geography × time × food taxonomy × contaminant cell. The primary decision is absolute quantile/threshold compliance with uncertainty. Ranking is optional monitoring triage, not the task's principal output.

Allowed claim in this run: modelling behavior on synthetic scenarios. Actual Chinese safety, legal compliance, and probability claims are forbidden.

## 4. Indicator System

The core chain is food intake `I`, contaminant concentration `C`, daily exposure `D=ΣIC`, extreme quantile `q`, standard `T`, point ratio `ρ=q/T`, and uncertainty-upper ratio `ρ_U`. Population affects triage; monitoring coverage/effective sample size describe evidence quality. Quality cannot offset hazard.

## 5. Indicator Provenance

Every composite retains raw inputs, formula, unit, direction, source type, and aggregation level. `point_ratio` and `upper_ratio` overlap; their joint additive baseline use is flagged `DOUBLE_WEIGHTING_RISK`. The primary does not add them.

## 6. Data / External Sources

`NO_EXTERNAL_DATA_USED`. Operational data and standards are listed as required-but-not-acquired. No modern standard was silently substituted for the 2007 question. All numeric outputs are synthetic and seeded.

## 7. Baseline

The runnable exposure baseline resamples observed synthetic intake/concentrations, codes nondetects as zero, and takes the `0.99999` quantile from two million draws. It returns about `5,305` versus the known-parameter synthetic oracle `13,162`, an error of about `-59.7%`.

The secondary baseline uses equal weights only inside the hard class. Its order is `North-A > West-B > Coast-C > South-A > East-B > Central-C`.

## 8. Normalization

Formal compliance uses only unit conversion and the fixed-threshold ratio `q/T`; it is not candidate-set normalized. Baseline current-set min-max records cost/benefit direction, zero/constant handling, outlier policy, and candidate-set dependence. Fixed-bound and vector alternatives were run.

## 9. Weighting

Primary hard/lexicographic evaluation has no numeric weights. Baseline weights are four equal `0.25` neutral comparison weights, normalized to one, not expert/policy/data importance. No expert judgments, entropy weights, AHP matrix, or TOPSIS weights were invented.

## 10. Hard / Soft Criteria

`ρ>1` is a hard point violation. `ρ≤1≤ρ_U` is uncertain, including the boundary. `ρ_U<1` is compliant only under the declared model/evidence. Monitoring coverage, sample size, and population cannot cancel the hard gate.

## 11. Primary Evaluation Model

The primary chain uses design-aware intake modelling, a left-censored contaminant likelihood, a mass-conserving taxonomy crosswalk, conditional integration of unpaired samples, population transport weights, exposure simulation/tail modelling, full uncertainty, and a hard gate. Optional triage is lexicographic by class, upper ratio, point ratio, and population.

## 12. Composite Score / Ranking

Synthetic primary order: `Coast-C > North-A > West-B > South-A > East-B > Central-C`. The first three are violations, South-A is uncertain, and the last two are compliant under model. Coast-C/North-A are a near tie. Baseline/primary Spearman is `0.829`; top-three overlap is `1.00`.

## 13. Risk Interpretation

Risk is the distribution/tail of daily intake. `q` is an exposure quantile; `ρ` is a threshold ratio; the baseline score is relative; the optional rank is triage priority. None is an absolute safety probability. An exceedance probability requires a validated probability model and is a distinct output.

## 14. Dominance / Monotonicity Checks

Benefit improvement, cost direction, unit rescaling, dominance, and hard-constraint tests all pass. The safer dominating synthetic option has a higher safety score and lower action priority; the worse option cannot overtake through quality compensation.

## 15. Weight Sensitivity

±10%/±20% one-at-a-time baseline weight changes keep top-three overlap at `1.00` and minimum Spearman at `0.943`, but switch first place between North-A and West-B. The weighted winner is unstable.

## 16. Normalization Sensitivity

Min-max, fixed bounds, and vector normalization produce the same baseline order in this scenario. This stability is relative and does not make scores absolute.

## 17. Indicator-Set Sensitivity

Deleting coverage, population, or upper ratio changes ordering inside the violation class; minimum Spearman is `0.943`, top-three overlap `1.00`. Exact winner claims are unsupported.

## 18. Rank Stability

Adding a dominated alternative reverses no existing pair under baseline or primary. Hard class/top-three are stable; exact baseline winner and primary top-two ordering are not robust enough for a unique recommendation. `RANKING_STABILITY=PARTIAL`.

## 19. Threshold / Classification

Threshold one is derived from `q/T`; no arbitrary `0.3/0.6` grades are used. A real `T` must come from a versioned applicable regulation/authority. The run's illustrative `T=0.95×oracle` is `ASSUMED_SYNTHETIC` only.

## 20. Uncertainty

Five 400,000-draw primary tail repeats range about `9,301–11,726`; contamination log-scale ±10% scenarios give about `6,918–18,834`. The primary point estimate remains about `-15.2%` below the oracle. A point-only safe claim is rejected; the synthetic case is uncertain.

## 21. Policy / Improvement Recommendations

Use probability sampling, record LOD/method/design, fit censoring rather than zeros, version a mass-conserving taxonomy crosswalk, model dependence/transport, validate the extreme tail, and gate on an uncertainty upper bound. Recommend action from hard violation and risk driver, not “rank one” alone.

## 22. Final Results

All source-defined components are modelled conditionally; baseline, primary, sensitivity, and synthetic contracts were actually run. No real-world result is claimed. Censored modelling materially improves the synthetic tail estimate but remaining uncertainty prevents a precise operational conclusion.

## 23. Skill Strengths

The frozen Skill correctly required problem understanding before model choice, a runnable equal-weight evaluation baseline, consistent protocols, evidence/run binding, direction/normalization/weight provenance, hard-versus-soft awareness, missing/extreme handling, rank-reversal checks, and rank stability metrics. These guards prevented a method zoo and made the run auditable.

## 24. Skill Weaknesses

The evaluation family remains a short algorithm-oriented reference. It does not require an evaluation-target contract before weighting and does not explicitly distinguish absolute probability/quantile, regulatory compliance, relative score, rank, and class or require threshold provenance. Its generic candidate list can therefore be activated before output semantics are locked.

## 25. First Meaningful Failure

`EVALUATION_OUTPUT_SEMANTICS_CONTRACT_MISSING`.

At the first evaluation-model selection point, the frozen Skill did not itself force the model to state that 2007A needs an absolute `0.99999` exposure quantile plus hard-standard comparison rather than a relative composite rank. The user-supplied stress-test instructions supplied that missing guard.

## 26. Failure Classification

`P0`. Confusing a relative score with probability/compliance, or letting ordinary criteria compensate a safety threshold, can invalidate the formal evaluation conclusion.

## 27. Generalizable Gap Candidate

`GENERALIZABLE_EVALUATION_GAP_FOUND`.

Gate check:

1. frozen Skill lacks the mandatory contract: yes;
2. 2007A materially depends on it: yes;
3. not tied to a missing algorithm: yes;
4. applies beyond food safety: yes;
5. transfers to supplier, city, ecological, education, enterprise, credit, and safety evaluation: yes;
6. affects correctness/stability: yes;
7. expressible as a lightweight rule: yes;
8. needs no evaluation platform: yes.

Candidate rule for later human consideration: before any weighting/normalization, record evaluation object, decision question, stakeholder/scope, output semantics (`absolute_probability`, `absolute_quantile`, `regulatory_compliance`, `relative_score`, `rank`, or `class`), hard thresholds and provenance, and allowed claim; forbid conversion of relative composite scores into probability/compliance and apply hard gates before compensatory aggregation.

No Skill change is made in this blind run.

## 28. Remaining Uncertainty

Real sampling frames, standards, units, LODs, food mappings, dependence, transport, and tail model coverage remain unknown. The source's distribution-skew wording is not enough to choose a family. Real-world classification remains unavailable.

## 29. Historical Integrity

Initial `HEAD=bd28c3fe87b4f1fb8cc45217f5c79572d7989a84`; initial `skill/` tree=`2b29e8ffa7c15d33bf81e675e8f1dcb240c226a6`. Final integrity and repository tests are recorded under `validation-results/`. Only this `run-001` directory is in the intended commit. 2017F was neither modified nor redone; excellent papers were not accessed.

Existing environment/repository conditions are recorded, not repaired: `DEFAULT_PYTEST_ENVIRONMENT_ISSUE_EXISTING`, ignored `.tmp/github-publish-checkout`, frozen path/smoke constraints, and pre-existing historical artifacts.

## 30. Final Decision

`GENERALIZABLE_EVALUATION_GAP_FOUND`

Single TOP-1 gap: `EVALUATION_OUTPUT_SEMANTICS_CONTRACT_MISSING` (`P0`).

The blind run itself is valid and complete for the declared synthetic/conditional claim boundary. Stop here for human review; do not modify the Skill, access excellent solutions, perform post-hoc comparison, or begin a ninth problem.
