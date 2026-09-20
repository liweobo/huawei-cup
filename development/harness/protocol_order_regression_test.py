"""Protocol identity must canonicalize mapping keys and preserve sequence order.

Regression for ORDERED_PROTOCOL_NORMALIZATION_FALSE_NEGATIVE: the normalizer
previously sorted every list, so a reordered event/validation pipeline compared
equal to the original plan and the protocol-change guard passed silently.
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from skill.scripts.runtime_provenance import (
    apply_protocol_change,
    normalize_protocol,
    protocols_differ,
    validate_experiment_record,
)


def check(label: str, ok: bool, failures: list[str]) -> None:
    print(f"{'PASS' if ok else 'FAIL'} | {label}")
    if not ok:
        failures.append(label)


def main() -> int:
    failures: list[str] = []

    # A. Mapping key order carries no semantics.
    check(
        "A mapping key reorder is ignored",
        not protocols_differ({"a": 1, "b": 2}, {"b": 2, "a": 1}),
        failures,
    )

    # B. Scalar sequence order is semantic.
    check(
        "B ordered scalar list reorder is detected",
        protocols_differ(["A", "B", "C"], ["B", "A", "C"]),
        failures,
    )

    # C. Identical sequences are equal.
    check(
        "C identical list is unchanged",
        not protocols_differ(["A", "B", "C"], ["A", "B", "C"]),
        failures,
    )

    # D. Sequence of mappings preserves element order.
    check(
        "D list-of-dict reorder is detected",
        protocols_differ([{"step": "load"}, {"step": "fit"}], [{"step": "fit"}, {"step": "load"}]),
        failures,
    )

    # E. Nested mapping key reorder alone is not a change.
    check(
        "E nested mapping key reorder is ignored",
        not protocols_differ([{"type": "fit", "seed": 1}], [{"seed": 1, "type": "fit"}]),
        failures,
    )

    # F. Nested ordered pipeline keeps order even though inner mappings canonicalize.
    check(
        "F nested ordered pipeline reorder is detected",
        protocols_differ(
            [{"type": "scale"}, {"type": "PCA"}, {"type": "model"}],
            [{"type": "PCA"}, {"type": "scale"}, {"type": "model"}],
        ),
        failures,
    )

    # G. Tuple order is semantic.
    check(
        "G tuple order is detected",
        protocols_differ(("receive", "review"), ("review", "receive")),
        failures,
    )
    check(
        "G identical tuple is unchanged",
        not protocols_differ(("receive", "review"), ("receive", "review")),
        failures,
    )

    # H. Duplicate elements must not be collapsed as a set.
    check(
        "H duplicate sequence reorder is detected",
        protocols_differ(["A", "A", "B"], ["A", "B", "A"]),
        failures,
    )

    # Extra: mixed sequence with only nested key-order differences stays equal.
    check(
        "I mixed sequence with nested key reorder is unchanged",
        not protocols_differ(["A", {"b": 2, "a": 1}, "C"], ["A", {"a": 1, "b": 2}, "C"]),
        failures,
    )

    # Non-inventory pipeline: proves the fix is not hardcoded to inventory stages.
    check(
        "Non-inventory signal pipeline reorder is detected",
        protocols_differ(
            {"stages": ["detrend", "window", "fft"]},
            {"stages": ["fft", "window", "detrend"]},
        ),
        failures,
    )
    check(
        "Non-inventory ML preprocessing reorder is detected",
        protocols_differ(
            {"pipeline": ["impute", "scale", "fit"]},
            {"pipeline": ["scale", "impute", "fit"]},
        ),
        failures,
    )

    # normalize_protocol keeps sequence positions and canonicalizes mapping keys.
    check(
        "normalize_protocol preserves sequence order",
        normalize_protocol(["z", "a"]) == ["z", "a"],
        failures,
    )
    check(
        "normalize_protocol canonicalizes mapping keys",
        normalize_protocol({"b": 1, "a": 2}) == {"a": 2, "b": 1},
        failures,
    )
    check(
        "normalize_protocol represents tuples as ordered lists",
        normalize_protocol(("b", "a")) == ["b", "a"],
        failures,
    )

    # I (validation-stage reorder) end to end through the record contract.
    base = {
        "experiment_id": "EXP-ORDER-001",
        "run_id": "run-order",
        "created_at": "2026-09-20T00:00:00Z",
        "problem": "generic",
        "question": "Q1",
        "status": "OBSERVED",
        "updated_by_workflow": "validate_model",
        "planned_protocol": {"validation": [{"type": "holdout"}, {"type": "leave_one_group_out"}]},
        "executed_protocol": {"validation": [{"type": "holdout"}, {"type": "leave_one_group_out"}]},
        "change_reason": "",
        "comparable_to_original_plan": True,
        "input_artifacts": ["data.csv"],
        "code_artifacts": ["run.py"],
        "output_artifacts": ["metrics.json"],
        "random_seed": 7,
        "metrics": {"MAE": 1.0},
        "evidence_ids": ["EV-1"],
    }
    unchanged = apply_protocol_change(base)
    check("J unchanged protocol computes protocol_changed=false", unchanged["protocol_changed"] is False, failures)
    check("J unchanged record validates", not validate_experiment_record(unchanged), failures)

    reordered = copy.deepcopy(base)
    reordered["executed_protocol"] = {"validation": [{"type": "leave_one_group_out"}, {"type": "holdout"}]}
    reordered["change_reason"] = "Validation stages were reordered."
    changed = apply_protocol_change(reordered)
    check("J reordered validation stages compute protocol_changed=true", changed["protocol_changed"] is True, failures)

    # J. A parameter change with identical sequence is still a change.
    check(
        "J parameter change is detected",
        protocols_differ(["A", "B"], ["A", "C"]),
        failures,
    )

    # OBSERVED records with a changed protocol must still be gated.
    undisclosed = copy.deepcopy(reordered)
    undisclosed["protocol_changed"] = False
    check(
        "J OBSERVED sequence reorder without declaration is rejected",
        any("protocol_changed" in error for error in validate_experiment_record(undisclosed)),
        failures,
    )

    print(f"\nProtocol Order Regression Test: {'PASS' if not failures else 'FAIL'} ({len(failures)} failures)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
