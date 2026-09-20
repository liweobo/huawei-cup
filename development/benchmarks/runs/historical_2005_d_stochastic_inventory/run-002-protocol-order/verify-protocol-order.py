"""Targeted regression: the 2005D event-order counterexample must now be detected.

This does not re-solve 2005D. It reads the frozen run-001 probe and the frozen
run-001 experiment record, then re-evaluates them against the corrected
skill/scripts/runtime_provenance.py.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[5]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from skill.scripts.runtime_provenance import (
    apply_protocol_change,
    protocols_differ,
    validate_experiment_record,
)

FROZEN_RUN = ROOT / "development/benchmarks/runs/historical_2005_d_stochastic_inventory/run-001"
OUT = Path(__file__).resolve().parent / "results"


def main() -> int:
    probe = json.loads((FROZEN_RUN / "validation/ordered-protocol-probe.json").read_text(encoding="utf-8"))
    record = yaml.safe_load((FROZEN_RUN / "experiment-record.yaml").read_text(encoding="utf-8"))

    planned = probe["planned_order"]
    changed = probe["changed_execution_order"]

    observed_after_fix = protocols_differ(planned, changed)
    production_self_compare = protocols_differ(planned, planned)
    production_event_order = record["planned_protocol"]["event_order"]
    production_order_application = protocols_differ(production_event_order, list(reversed(production_event_order)))

    frozen_record_changed = protocols_differ(record["planned_protocol"], record["executed_protocol"])
    recomputed = apply_protocol_change(record)
    record_errors = validate_experiment_record(record)

    payload = {
        "benchmark_id": "historical_2005_d_stochastic_inventory",
        "run": "run-002-protocol-order",
        "purpose": "ORDERED_PROTOCOL_NORMALIZATION_READY targeted regression; does not re-solve 2005D",
        "reads": {
            "frozen_probe": str((FROZEN_RUN / "validation/ordered-protocol-probe.json").relative_to(ROOT)),
            "frozen_record": str((FROZEN_RUN / "experiment-record.yaml").relative_to(ROOT)),
        },
        "planned_order": planned,
        "changed_order": changed,
        "old_expected_protocol_changed": probe["expected_protocol_changed"],
        "old_observed_protocol_changed_before_fix": probe["observed_protocol_changed"],
        "new_protocols_differ": observed_after_fix,
        "detection_fixed": observed_after_fix is True and probe["observed_protocol_changed"] is False,
        "production_protocol_self_compare_changed": production_self_compare,
        "production_event_order": production_event_order,
        "production_order_reversal_detected": production_order_application,
        "frozen_record_planned_vs_executed_changed": frozen_record_changed,
        "frozen_record_protocol_changed_field": record.get("protocol_changed"),
        "recomputed_protocol_changed": recomputed["protocol_changed"],
        "frozen_record_still_validates": not record_errors,
        "frozen_record_validator_errors": record_errors,
        "tiny_event_counterexample_effect": probe["tiny_event_counterexample"],
        "status": "PASS",
    }

    checks = {
        "new_protocols_differ_is_true": observed_after_fix is True,
        "production_self_compare_unchanged": production_self_compare is False,
        "production_order_reversal_detected": production_order_application is True,
        "recomputed_matches_frozen_field": recomputed["protocol_changed"] == record.get("protocol_changed"),
        "frozen_record_still_validates": not record_errors,
    }
    payload["checks"] = checks
    if not all(checks.values()):
        payload["status"] = "FAIL"

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "protocol-order-regression.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    for name, ok in checks.items():
        print(f"{'PASS' if ok else 'FAIL'} | {name}")
    print(
        "\n2005D ordered-protocol targeted regression: "
        f"{payload['status']} "
        f"(old_observed={probe['observed_protocol_changed']} -> new_observed={observed_after_fix})"
    )
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
