# 2011B run-002 closure-gate targeted regression

This run validates the new generic closure capability against synthetic contracts. It is not a new 2011B physical simulation and does not alter `run-001` or the post-hoc reference benchmark.

## Checks

- A fully specified ODE-like forward model is `CLOSED_FOR_UNIQUE_NUMERICAL`.
- Missing initial state, geometry, or observation condition cannot produce a unique formal result.
- Missing initial state can fall back to `PARAMETRIC`.
- An explicit essential assumption produces `SCENARIO_ASSUMED` and requires provenance.
- A traceable derived quantity can close the model.
- Limited identifiability blocks unique parameter-estimation claims while allowing a forward claim when all forward inputs are fixed.
- An unverified cutoff produces `TERMINATION_RULE_UNVERIFIED`; verified refinement permits closure.
- Model-form discrepancy must be acknowledged separately from numerical convergence.
- A parametric result cannot pass the unique numerical claim gate.

The real execution output is `outputs/results.json`; all 12 cases passed. The synthetic tests are implemented in `development/tests/test_mechanism_closure.py` and use the same `skill/scripts/mechanism_closure.py` helper.

## Historical boundary

`run-001`, `reference-benchmark`, 2022C, 2023E and 2024C frozen assets are read-only. No additional 2011B paper was consulted and no 2011B solver was rerun.
