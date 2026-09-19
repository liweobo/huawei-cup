# Mechanism Model Closure Gate Fix Report

## 1. Skill Gap

The post-hoc 2011B benchmark identified a general gap: a mechanism equation can be mathematically correct while its essential geometry, initial state, forcing, interface, observation, material, or termination input is missing. The fix is `MECHANISM_MODEL_CLOSURE_GATE`.

## 2. Mechanism Closure Contract

Added `skill/templates/mechanism-closure.yaml` and the executable API in `skill/scripts/mechanism_closure.py`. The contract accepts a wrapper key `mechanism_closure` and records model target, scope, applicable requirement categories, provenance, identifiability, termination verification, evidence, closure status and allowed claim level.

## 3. Requirement Categories

The gate covers geometry/domain, state/initial condition, boundary/interface, forcing/input, material/constitutive law, observation/output condition and termination/horizon. Categories are optional when not applicable; essential requirements are not optional.

## 4. Closure Status

The helper derives `CLOSED_FOR_UNIQUE_NUMERICAL`, `PARAMETRIC`, `SCENARIO_ASSUMED`, `PARTIAL` or `UNVERIFIED`. Explicit `PARTIAL` and `UNVERIFIED` declarations remain conservative overrides.

## 5. Assumption / Parameterization Rules

`GIVEN`, `DERIVED`, `EXTERNAL`, `ASSUMED`, `PARAMETERIZED` and `MISSING` are distinct source types. An essential assumption requires reason, plausible range and result dependency. A missing input with a natural parameterization falls back to `PARAMETRIC`; it is never silently hardcoded.

## 6. Identifiability Rule

`PASS`, `LIMITED`, `NON_IDENTIFIABLE` and `UNVERIFIED` are recorded separately. Limited identifiability blocks unique parameter-estimation claims, while a forward calculation with genuinely fixed inputs may still be closed under its declared model.

## 7. Numerical Termination Rule

Essential reflection order, series cutoff, iteration limit, integration domain, escape rule or time horizon must have refinement or tail evidence. Without it the contract is `UNVERIFIED` and the reviewer emits `TERMINATION_RULE_UNVERIFIED`.

## 8. Closure vs Validity

`CLOSED_FOR_UNIQUE_NUMERICAL` means unique within the declared model and assumptions. It does not mean the mechanism is the unique physical explanation, experimentally validated, or free from model-form error.

## 9. Model-Form Uncertainty

A contract can record materially different reasonable approximations through `model_form_uncertainty`. Numerical convergence is kept separate from model validity; an acknowledged discrepancy does not itself invalidate either closed model.

## 10. Claim Gate

The strongest claim is mapped by status: unique under model, parametric result, scenario result, partial result, or no formal result. A parametric, scenario, partial or unverified result cannot be published as `UNIQUE_NUMERICAL_UNDER_MODEL`.

## 11. Reviewer Guards

The helper recognizes `MECHANISM_CLOSURE_UNVERIFIED`, `SILENT_CLOSURE_ASSUMPTION`, `UNSUPPORTED_UNIQUE_NUMERICAL_CLAIM`, `TERMINATION_RULE_UNVERIFIED` and `MODEL_FORM_UNCERTAINTY_IGNORED`. Reviewer and write-paper workflows now require the closure reference for mechanism work.

## 12. Synthetic Tests

Cases A-L cover fully closed ODE, missing initial state, parameterized fallback, explicit scenario, silent geometry assumption, derived geometry, missing observation, limited identifiability, unverified termination, verified termination, model-form discrepancy and claim enforcement. The repository pytest file has 13 tests, including an explicit partial-status case.

## 13. 2011B Q1 Closure

The frozen Blind Run Q1 remains `PARAMETRIC`: entry position/equivalent initial geometric state and wedge scale are not uniquely given. The fix confirms that a tip-entry value must not be silently inserted and that the result cannot be presented as a unique numerical trajectory.

## 14. 2011B Q2 Closure

Under the frozen declared simplified power-sum mechanism, Q2 is `CLOSED_FOR_UNIQUE_NUMERICAL` for the stated geometry, source trajectory, reflectivity cases, receiver region and explicit assumptions. This is scoped to the declared model; it does not certify the real chamber mechanism.

## 15. 2011B Termination Evidence

The frozen Q2 evidence already contains image-order refinement through `K=40`, area quadrature refinement, time-grid refinement and an all-time upper certificate. Therefore `numerical_termination_verified: true` is appropriate for the declared model. The historical results remain rho=0.50 gamma about `0.39246-0.39486` and rho=0.05 gamma about `0.02967-0.02974`, with upper certificate `0.02986864 < 0.03`.

## 16. Targeted Regression

`run-002-closure-gate` executed the same helper on 12 synthetic cases. `outputs/results.json` reports `passed: true` and `case_count: 12`. No 2011B physical solver or additional paper was read.

## 17. Existing Capability Regression

Behavior contracts pass for all 10 existing routes. Routing remains 10 routes. The isolated Python suite passes after adding the closure tests. The default full-worktree pytest environment retains its known `.tmp/github-publish-checkout` module-discovery issue; the pre-existing smoke scan also finds a historical 2022C unfinished marker, neither introduced by this fix.

## 18. Historical Integrity

`run-001` and `reference-benchmark` are read-only. The frozen 2022C, 2023E and 2024C assets are unchanged. No additional 2011B literature was consulted. No PDF, OCR cache, `.tmp`, `__pycache__` or temporary numerical artifact is part of the intended commit.

## 19. Remaining Mechanism Risks

The gate does not supply electromagnetic formulas, FEM/FDTD, a universal solver, a material database, an uncertainty framework or an identifiability framework. Forward model validity, omitted mechanisms, complex material response, calibration and experimental validation remain domain work and must be recorded as such.

## 20. Final Status

`MECHANISM_MODEL_CLOSURE_READY`.

The Skill now has a reusable contract, executable status/claim checks, reviewer guards, workflow integration and a targeted 2011B regression. No second mechanism gap was opened.
