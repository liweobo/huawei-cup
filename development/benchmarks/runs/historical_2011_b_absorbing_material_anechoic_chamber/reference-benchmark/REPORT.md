# 2011B Reference Benchmark Report

## 1. Scope and integrity

This is the post-hoc excellent-solution benchmark for `historical_2011_b_absorbing_material_anechoic_chamber`. It follows the frozen Blind Run `run-001`. The starting HEAD was `991e8aa93f1383f5ae94f5ba90d6d02c5d9f91b1`; the starting `skill/` tree hash was `ea0be7810800d452c1703407becc9b45a5e51722`. No Skill file, Blind Run file, or frozen 2022C/2023E/2024C asset was edited.

The exact reference directory was read after the Blind Run was frozen. Eleven PDFs were downloaded, hashed and extracted to ignored temporary storage. The source ledger records URLs, hashes, extraction quality and confidence. Award levels remain `UNKNOWN`; the repository label was not treated as an official ranking.

## 2. Reference quality

All 11 papers were fully reviewed at the text level. B10319002 and B10386003 were additionally rendered and visually checked at formula/table pages. Extraction was high for 9 papers and medium/low for B10319002; the latter's comparable result range was taken from visual page 14. No reference PDF is committed.

## 3. Problem formulation and mechanism families

The references agree on the broad problem: geometric reflection in a wedge for Q1, and reflected/direct power in a finite chamber for Q2. They do not agree on one governing approximation. The Q2 families are Fresnel-Huygens, radiosity, view factors, image paths, one-bounce integrals, weighted limiting models and Monte Carlo.

This heterogeneity is material. For rho=0.05, reported gamma values range approximately from 0.0035 to 0.0218 in the reference set, while the frozen Blind Run gives 0.02967-0.02974 under its finite-area image-path power-sum model. The spread is model-form discrepancy, not numerical noise.

## 4. Q1 closure finding

Q1 needs an entry position and wedge scale to produce a unique numerical trajectory. Several papers fix tip or vertex entry; others sample or parameterize entry position. The references therefore support the Blind Run's decision to add `y0` explicitly and return a parametric result. The issue is general: a mechanism model cannot be called uniquely solved when its initial state, source distribution or observation condition is missing.

## 5. Q2 comparison

The stable qualitative result is that rho=0.50 fails the `gamma <= 0.03` requirement and rho=0.05 generally passes under the chosen approximations, with the minimum near `t=2 s`. The quantitative result is not consensus. B10699002 alone reports about 0.344 for its geometric model versus about 0.15 for its Huygens model at rho=0.50, illustrating that adding a different mechanism layer changes the answer materially.

The Blind Run is numerically well checked for its own assumptions: image order, area quadrature, time grid and explicit-path agreement were tested, and an all-time upper certificate was obtained. This is evidence of numerical correctness, not evidence that the selected mechanism is the physical truth.

## 6. Validation and parameter discipline

The references rely mainly on energy balance, symmetry, limiting cases, tables and refinement. None provides independent chamber measurements. Most use the scalar effective rho cases from the statement; complex phase, frequency dependence and scattering are not identifiable. The Blind Run's provenance and numerical-error/model-error separation are stronger than the median reference presentation, while its real-world validation limitation is the same.

## 7. First meaningful failure and gap decision

The first meaningful failure remains `MECHANISM_MODEL_CLOSURE_UNDER_SPECIFIED_INPUTS`, classified P1. Post-hoc references confirm it and show the practical consequences of silently choosing different closures. The single TOP-1 generalizable gap is `MECHANISM_MODEL_CLOSURE_GATE`.

The gate should require explicit source/initial state, interface and receiver conditions, material-law sufficiency, and a verified termination rule before a mechanism model is promoted to a unique numerical answer. Approximation ladders and tail checks belong inside that gate; they are not selected as a second gap.

## 8. Final decision

`GENERALIZABLE_MECHANISM_GAP_FOUND`.

This is not a claim that the references are ground truth or that the Blind Run is invalid. It is a post-hoc diagnosis that the current Skill needs a domain-neutral closure decision before mechanism simulation can be considered fully specified. The Skill remains unchanged in this benchmark.

## 9. Historical integrity

`excellent_solutions_accessed=true` only for this post-hoc phase; `skill_modified=false`; `run-001` remains byte-identical to its pre-reference integrity record. The prohibited 2011B excellent-paper tree was not accessed before the Blind Run and no problem-specific solution source outside the designated reference directory was used.

```text
2011B_REFERENCE_BENCHMARK_COMPLETE
reference_quality: 11 papers discovered; 11 fully reviewed; 2 visually verified
papers_discovered: 11
papers_fully_reviewed: 11
award_levels_verified: 0 (UNKNOWN for all)
problem_formulation_level: PARTIAL_UNDER_SPECIFIED_Q1_ENTRY
physical_consistency_level: QUALITATIVE_CONSENSUS
model_closure_level: PARTIAL; materially different added assumptions
numerical_verification_level: MIXED; strongest in B10699002 and the frozen Blind Run
parameter_discipline_level: PARTIAL; effective scalar rho only
mechanism_depth_level: HETEROGENEOUS
overall_skill_level: VALID_WITH_P1_CLOSURE_GAP
top_generalizable_gap: MECHANISM_MODEL_CLOSURE_GATE
final_decision: GENERALIZABLE_MECHANISM_GAP_FOUND
recommended_next_action: human-review this post-hoc diagnosis, then decide separately whether to update the Skill
```
