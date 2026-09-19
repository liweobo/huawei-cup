# Mechanism Closure Gate

Use this reference only when a subproblem uses a mechanism, physical law, dynamic state, simulation, or numerical propagation. It is a closure decision, not a physics solver or a validity certificate.

## Contract

Create a `mechanism_closure` contract before promoting a mechanism model to a formal numerical answer. The contract records requirements in only the categories that apply:

- geometry/domain;
- initial/state condition;
- boundary/interface condition;
- forcing/input;
- material/constitutive law;
- observation/output condition;
- termination/horizon.

Each requirement records `name`, `meaning`, `required_for`, `source_type`, `source`, `value_or_parameter`, `unit`, `status`, `essential`, and `assumption_reason`. Allowed `source_type` values are `GIVEN`, `DERIVED`, `EXTERNAL`, `ASSUMED`, `PARAMETERIZED`, and `MISSING`.

Use `DERIVED` only when the derivation is written and traceable to the problem facts. Use `EXTERNAL` for general domain knowledge, not for a problem-specific answer. Use `ASSUMED` only with a reason, plausible range, result dependency, and materiality check. Use `PARAMETERIZED` when the missing quantity can remain an explicit parameter. Never silently replace `MISSING` with a convenient constant.

## Status and claim gate

Derive one of:

- `CLOSED_FOR_UNIQUE_NUMERICAL`: every essential requirement is resolved under the declared model and numerical termination is verified;
- `PARAMETRIC`: an essential input is intentionally retained as a parameter;
- `SCENARIO_ASSUMED`: an essential input is supplied as an explicit assumption;
- `PARTIAL`: only part of the mechanism or requested output is closed;
- `UNVERIFIED`: an essential input, observation condition, or termination rule cannot be verified.

The status is internal mathematical closure under the declared model. It does not claim that the model is the unique physical mechanism or that experiments validate it.

Allowed claims are correspondingly limited:

| closure status | strongest allowed claim |
|---|---|
| `CLOSED_FOR_UNIQUE_NUMERICAL` | `UNIQUE_NUMERICAL_UNDER_MODEL` |
| `PARAMETRIC` | `PARAMETRIC_RESULT` |
| `SCENARIO_ASSUMED` | `SCENARIO_RESULT` |
| `PARTIAL` | `PARTIAL_RESULT` |
| `UNVERIFIED` | `NO_FORMAL_RESULT` |

If an essential requirement is missing, do not publish a unique numerical claim. Prefer a parameterized result; otherwise use an explicit scenario, partial result, or no formal result. A scenario result must say `CONDITIONAL ON ASSUMPTION`.

## Identifiability

Record `identifiability_status` as `PASS`, `LIMITED`, `NON_IDENTIFIABLE`, or `UNVERIFIED`. Limited identifiability does not automatically invalidate a forward calculation with genuinely given parameters, but it blocks a claim of unique high-precision parameter estimates. Do not use convergence or a good fit to conceal non-identifiability.

## Approximation and numerical closure

State retained mechanisms, omitted mechanisms, and the regime of validity. Keep the comparison small: a baseline, the primary mechanism model, and at most one justified refinement. If reasonable approximations materially disagree, record `MODEL_FORM_UNCERTAINTY`; numerical convergence does not make the physical model unique.

Any series cutoff, reflection order, iteration limit, integration domain, time horizon, or escape rule is part of closure. Set `numerical_termination_verified: true` only after refinement stability or a defensible tail bound. A fixed cutoff without evidence is `TERMINATION_RULE_UNVERIFIED`.

## Reviewer guards

- `MECHANISM_CLOSURE_UNVERIFIED`: essential state, geometry, interface, forcing, observation, or termination input is missing or unverifiable.
- `SILENT_CLOSURE_ASSUMPTION`: an essential assumed value lacks explicit provenance or sensitivity information.
- `UNSUPPORTED_UNIQUE_NUMERICAL_CLAIM`: a parametric, scenario, partial, or unverified result is presented as unique.
- `TERMINATION_RULE_UNVERIFIED`: a formal numerical result depends on an unverified truncation or termination rule.
- `MODEL_FORM_UNCERTAINTY_IGNORED`: materially different reasonable approximations exist but the claim presents one as physical truth without qualification.

The gate is active for mechanism/physical/dynamic simulation only. It does not replace the existing temporal, grouped-validation, optimization feasibility, or structured-improvement contracts for other task families.
