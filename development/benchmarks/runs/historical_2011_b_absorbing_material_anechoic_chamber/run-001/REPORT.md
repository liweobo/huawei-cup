# 2011B Fourth-Problem Blind Run

Benchmark: `historical_2011_b_absorbing_material_anechoic_chamber`
Run: `run-001`
Family: `MECHANISM_MODELING_AND_NUMERICAL_SIMULATION`

## 1. Source Provenance

Source: https://github.com/zhanwen/MathModel/tree/master/国赛试题/2011年研究生数学建模竞赛试题
File: `2011B题吸波材料与微波暗室问题的数学建模.doc`
Git blob SHA: `02ddbe988aa8205e8493d46253f34e8641ae01b5`
Bytes: `1773056`
SHA256: `c44d22cb08b5f868357b0fdbd7bdaec1db4b7db1208f40e8324c5eb0716ede89`
Retained at `source/2011B题吸波材料与微波暗室问题的数学建模.doc`.

The source directory contained no separate B attachment. The excellent-paper tree and every problem-specific solution, blog, code or answer source were not accessed.

## 2. Problem Facts

Q1 requests a simple geometric-optics model for an infinite wedge: final ray direction, reflection count and intensity. Q2 requests the reflected/direct power ratio `gamma` in a `B=18 m, L=15 m, H=14 m` chamber with `R=14 m, b=1 m, s=0.3 m, beta=45 deg`, over four seconds, under `gamma<=0.03`; it gives flat `rho=0.50` and then effective `rho=0.05`. Facts, formulas, parameters, figures and extraction status are frozen in `problem-facts.md`.

## 3. External Domain Knowledge

Only general knowledge was used: OpenStax specular reflection for `u'=u-2(u dot n)n`, and NumPy Gauss-Legendre quadrature documentation. URLs, claims, purposes, hashes and confidence are in `domain-sources.md`. No historical solution source was used.

## 4. Quantity / Unit Audit

`rho` and `gamma` are dimensionless power ratios; intensity is W/sr, power W, irradiance/exitance W/m2, geometry m and motion time s. Reflection factors multiply as power ratios; no amplitude squaring is applied. The implemented equations are dimensionally closed. **PASS.** See `quantity-ledger.md`.

## 5. Assumptions

Smooth specular interfaces, no diffraction/scattering, quasi-static snapshots, forward cosine emission, incoherent power summation and nonperturbing receiver. Q1 adds an entry coordinate because the statement gives no entry point. Assumptions and provenance are separated in `assumptions.md`.

## 6. Subproblem Decomposition

Q1: exact 2D event trace and 3D extruded-wedge model. Q2: direct plus one-bounce baseline, then finite-area six-wall repeated reflection using unfolded receiver images. Each model has explicit state, inputs, outputs, geometry, interfaces and validation in `mathematical-model.md`.

## 7. Baseline Model

One-bounce Q2 gives `gamma=0.2889622` for `rho=0.50` and `0.0288962` for `rho=0.05` at `t=2 s`. This baseline is retained beside the multi-reflection model.

## 8. Mechanism Model

Q1 propagates `(p,u,w,N)` between two wedge facets and an escape plane. Q2 integrates `I_N max(a dot u,0)|u_y|W/D^2` over the quiet square, with image-path weight `(rho|u_x|)^Nx (rho|u_y|)^Ny (rho|u_z|)^Nz`. All prior wall hits are explicit; the receiver is terminal.

## 9. Parameter Provenance

Room data, motion data and both rho values are `GIVEN`; `d=2h tan(alpha)` and source position are `DERIVED`; `I*=1 W/sr` is `ASSUMED` normalization and cancels from gamma; quadrature, time grid and K are numerical controls. No complex material parameters are estimated. Formal provenance: **PASS**; complex-response identifiability: limited.

## 10. Boundary / Interface Conditions

Wedge facet equations, escape policy and apex `EDGE_UNDEFINED` policy are explicit. Chamber has six Cartesian reflecting planes, mirror paths, `rho|u dot n|` per prior hit and terminal quiet-zone reception. **PASS.**

## 11. Numerical Method

Python 3.12.10, NumPy 2.5.2, SciPy 1.18.1. Q1 ran 144 scenarios and 256/512/1024 landing diagnostics. Q2 used K through 40, quadrature orders 1/3/5/9, 81/161 time grids and an all-time derivative-bound certificate. Logs and code are retained.

## 12. Real Simulation Results

For `rho=0.50`, `gamma` is `0.39245849` to `0.39485913`; it fails the requirement. Minimum is at `t=0` and `t=4 s` by symmetry; first reported minimum `t=0`.

For `rho=0.05`, `gamma` is `0.02966885` at `t=2 s` to `0.02973729` at endpoints. The all-time upper certificate is `0.02986864<0.03`; under this model it passes, with a narrow margin. Minimum is `t=2 s`. Source intensity doubling cancels from gamma.

## 13. Numerical Convergence

K=24 to 40 changes gamma by about `3.5e-11` for rho=0.50; K=8 to 16 changes it by about `2.7e-14` for rho=0.05. Quadrature order 3 to 9 changes checked ratios by about `6.9e-15`; 81 to 161 time-grid changes are below `4.5e-9`. **YES.**

## 14. Physical Sanity Checks

Unit norm, plane hits, equal angles, Q1 power balance, 3D/2D identity, explicit/image paths, monotonicity in rho, source-scale cancellation, motion symmetry and zero-reflection limits all pass. Full records are in `physical-sanity-checks.md` and `outputs/physical-checks.json`.

## 15. Calibration / Validation

No calibration or independent chamber measurement exists. Internal invariants, limiting cases, symmetry, path reconstruction and refinement are weaker validation evidence and do not certify a real chamber.

## 16. Sensitivity / Uncertainty

Rho is critical. A simulated +10% perturbation from 0.05 gives gamma about `0.03280`, failing the threshold. This is `SIMULATED_PERTURBATION`, not a measurement interval. Q1 geometry and entry distribution remain structural uncertainty.

## 17. Engineering Interpretation

The flat `rho=0.50` case is inadequate. The supplied effective `rho=0.05` case is conditionally adequate for this simplified power-sum model only. Real use needs measured angle/frequency/phase response, scattering and receiver validation.

## 18. Skill Strengths

The frozen Skill supported source provenance, baseline/model separation, structured records, units, real execution, convergence, physical checks, sensitivity labels and reviewer evidence discipline.

## 19. Skill Weaknesses

It did not force a mechanism closure gate for missing geometric initial conditions, nor provide a domain-neutral finite-area ray-power or all-time certificate template. These remain observations; Skill files were not changed.

## 20. First Meaningful Failure

`MECHANISM_MODEL_CLOSURE_UNDER_SPECIFIED_INPUTS`: Q1 lacks a ray entry coordinate and numerical wedge dimensions, so a unique numerical trajectory is unavailable. The run had to add `y0/d` and preserve a parametric result. Q2 remained computable.

## 21. Failure Classification

**P1.** The parametric result is usable, but numerical specificity is materially limited. No P0 failure occurred in the implemented model.

## 22. Generalizable Gap Candidate

Top 1: **MECHANISM_MODEL_CLOSURE_GATE**. A domain-neutral gate should check whether geometry, initial/boundary data, material state and observation location suffice for a unique calculation; otherwise downgrade to `PARAMETRIC`/`PARTIAL` or stop. Do not add a field-specific electromagnetic formula.

## 23. Remaining Uncertainty

Effective-material interpretation, Q1 entry distribution and wedge dimensions, coherent phase, diffraction, scattering and frequency dependence remain unresolved. The source reuses alpha for wedge and incidence notation; code disambiguates incidence as `a`.

## 24. Historical Integrity

`excellent_solutions_accessed=false`. `skill/` and frozen historical assets were unchanged. Original DOC is retained with SHA256. Temporary parser/cache files are excluded.

## 25. Final Decision

`GENERALIZABLE_MECHANISM_GAP_FOUND`.

The blind run is valid for the stated simplified model, with real results for Q1 and both Q2 materials, but exposes one P1 domain-neutral closure gap. No Skill repair was made.

```text
FOURTH_PROBLEM_BLIND_RUN_COMPLETE
problem: 2011B 吸波材料与微波暗室问题的数学建模
problem_family: MECHANISM_MODELING_AND_NUMERICAL_SIMULATION
skill_modified: false
excellent_solutions_accessed: false
subproblems_completed: Q1 parametric 2D/3D; Q2 flat rho=0.50; Q2 effective rho=0.05
dimensional_consistency: PASS
parameter_provenance: PASS
boundary_conditions: PASS
numerical_convergence_checked: YES
physical_sanity_checks: PASS
final_result_status: VALID
first_meaningful_failure: MECHANISM_MODEL_CLOSURE_UNDER_SPECIFIED_INPUTS
failure_level: P1
generalizable_gap_candidate: MECHANISM_MODEL_CLOSURE_GATE
recommended_next_action: human-review this run before any separate Skill change
```
