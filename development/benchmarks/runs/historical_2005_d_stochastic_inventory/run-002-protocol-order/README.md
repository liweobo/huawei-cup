# run-002-protocol-order

Targeted regression for `ORDERED_PROTOCOL_NORMALIZATION_FALSE_NEGATIVE`.

This run does not re-solve 2005D. It re-evaluates the frozen run-001 evidence against the
corrected `skill/scripts/runtime_provenance.py` to confirm that an ordered event protocol is no
longer treated as an unordered collection.

## Inputs (read-only, frozen)

- `../run-001/validation/ordered-protocol-probe.json`
- `../run-001/experiment-record.yaml`

run-001 is not modified by this regression.

## Check

```
python development/benchmarks/runs/historical_2005_d_stochastic_inventory/run-002-protocol-order/verify-protocol-order.py
```

## Result

`results/protocol-order-regression.json` records:

- `old_observed_protocol_changed_before_fix: false`
- `new_protocols_differ: true`
- `production_protocol_self_compare_changed: false` (a protocol still equals itself)
- `production_order_reversal_detected: true`
- `frozen_record_still_validates: true`

The planned order (integrate demand and holding -> receive and top up -> review/order) and the
changed order (receive and top up -> integrate demand and holding -> review/order) now compare as
different, which matches the causally different fulfilled/lost/inventory outcomes recorded in the
frozen one-unit counterexample.
