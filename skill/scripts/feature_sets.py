"""Small, explicit feature-set contracts and paired comparisons, not subset search.

Keep raw data and unfitted transforms in a training-fold pipeline. These guards
audit saved provenance; they cannot prove that an external caller logged truthfully.
"""
from __future__ import annotations

from copy import deepcopy
import re
from typing import Any

import numpy as np


CONTRACT_FIELDS = set("task prediction_setting unit_of_analysis target feature_groups baseline_feature_groups candidate_incremental_groups required_groups optional_groups excluded_groups exclusion_reason temporal_scope group_scope selection_method selection_scope comparison_protocol status".split())
GROUP_FIELDS = set("name description source columns_or_builder availability temporal_role entity_level dimension domain_rationale required_or_optional".split())
RECORD_FIELDS = set("feature_set_id feature_groups feature_columns baseline_feature_set incremental_groups removed_groups removals selection_method selection_scope sample_ids fold_ids model_family comparison_parent comparison_reason protocol".split())
CONTROL_FIELDS = set("target target_definition target_values temporal_cutoff random_seeds model_family hyperparameter_policy preprocessing_policy metric_definitions primary_metric target_type".split())
ORDINAL_METRICS = {"MAE", "RMSE", "Quadratic Weighted Kappa", "Accuracy", "Within-One-Level Accuracy"}
IMBALANCE_METRICS = {"ROC-AUC", "PR-AUC", "Balanced Accuracy", "Positive Class Recall", "Positive Class Precision", "Positive Class F1", "Specificity"}
METRIC_DIRECTIONS = {"MAE": False, "RMSE": False, "Brier Score": False,
    **{m: True for m in ORDINAL_METRICS | IMBALANCE_METRICS if m not in {"MAE", "RMSE"}}}


def _failure(code: str, detail: str) -> str:
    return f"{code}: {detail}"


def feature_set_errors(record: dict[str, Any]) -> list[str]:
    """Validate design, actual columns, availability and fit/split evidence.

    Optional extension to Experiment Record; ordinary experiments are unchanged.
    PLANNED records need the same design and fixed split, but no fabricated fit log.
    """
    c, s = record.get("feature_set_contract"), record.get("feature_set")
    errors: list[str] = []
    if not isinstance(c, dict) or not isinstance(s, dict):
        return [_failure("FEATURE_PROVENANCE_INCOMPLETE", "contract and feature_set are required")]
    for obj, required, name in ((c, CONTRACT_FIELDS, "contract"), (s, RECORD_FIELDS, "feature_set")):
        if required - obj.keys():
            errors.append(_failure("FEATURE_PROVENANCE_INCOMPLETE", f"{name} missing {sorted(required - obj.keys())}"))
    if errors:
        return errors
    groups = c["feature_groups"]
    if not isinstance(groups, list) or not groups or any(not isinstance(g, dict) for g in groups):
        return [_failure("FEATURE_PROVENANCE_INCOMPLETE", "declare meaningful feature groups")]
    by_name = {}
    for g in groups:
        missing = GROUP_FIELDS - g.keys()
        if missing or any(g.get(k) in (None, "", []) for k in GROUP_FIELDS):
            errors.append(_failure("FEATURE_PROVENANCE_INCOMPLETE", f"group {g.get('name')} lacks metadata"))
            continue
        builder = g["columns_or_builder"]
        cols = builder.get("columns") if isinstance(builder, dict) else None
        if not isinstance(cols, list) or not cols or len(set(cols)) != len(cols) or g["dimension"] != len(cols):
            errors.append(_failure("FEATURE_PROVENANCE_INCOMPLETE", f"{g['name']}: concrete columns/dimension required"))
            continue
        if g["name"] in by_name:
            errors.append(_failure("FEATURE_PROVENANCE_INCOMPLETE", "duplicate group name"))
        by_name[g["name"]] = g
        if builder.get("derived") and any(not builder.get(k) for k in ("inputs", "formula", "units")):
            errors.append(_failure("FEATURE_PROVENANCE_INCOMPLETE", f"{g['name']}: derived inputs/formula/units required"))
    if errors:
        return errors
    for key in ("baseline_feature_groups", "candidate_incremental_groups", "required_groups", "optional_groups", "excluded_groups"):
        if set(c[key]) - by_name.keys():
            errors.append(_failure("FEATURE_PROVENANCE_INCOMPLETE", f"unknown {key}"))
    selected = s["feature_groups"]
    if not selected or set(selected) - by_name.keys() or len(set(selected)) != len(selected):
        return errors + [_failure("FEATURE_PROVENANCE_INCOMPLETE", "unknown/empty/duplicate selected groups")]
    if set(selected) & set(c["excluded_groups"]):
        errors.append(_failure("FEATURE_PROVENANCE_INCOMPLETE", "excluded group used"))
    if set(c["required_groups"]) - set(selected):
        errors.append(_failure("FEATURE_PROVENANCE_INCOMPLETE", "required group missing"))
    if set(s["incremental_groups"]) != set(selected) - set(c["baseline_feature_groups"]):
        errors.append(_failure("FEATURE_PROVENANCE_INCOMPLETE", "incremental_groups disagrees with actual design"))
    if any(not c["exclusion_reason"].get(g) for g in c["excluded_groups"]):
        errors.append(_failure("FEATURE_PROVENANCE_INCOMPLETE", "exclusion reason missing"))
    allowed = {col for g in selected for col in by_name[g]["columns_or_builder"]["columns"]}
    actual = set(s["feature_columns"])
    if not actual or len(actual) != len(s["feature_columns"]) or actual - allowed:
        errors.append(_failure("FEATURE_PROVENANCE_INCOMPLETE", "actual columns outside declared groups or duplicated"))
    baseline = {col for g in c["baseline_feature_groups"] if g in by_name for col in by_name[g]["columns_or_builder"]["columns"]}
    removed = (baseline | allowed) - actual
    declared = {r.get("column"): r for r in s["removals"] if isinstance(r, dict)}
    for col in removed:
        r = declared.get(col, {})
        if r.get("status") != "REMOVED_FROM_BASELINE" or not str(r.get("removal_reason", "")).strip():
            errors.append(_failure("UNCONTROLLED_FEATURE_SET_COMPARISON", f"{col} removed without REMOVED_FROM_BASELINE and removal_reason"))
    if set(declared) != removed:
        errors.append(_failure("FEATURE_PROVENANCE_INCOMPLETE", "removal log disagrees with actual columns"))
    missing_groups = set(c["baseline_feature_groups"]) - set(selected)
    if set(s["removed_groups"]) != missing_groups:
        errors.append(_failure("FEATURE_PROVENANCE_INCOMPLETE", "removed_groups disagrees with baseline"))
    for g in selected:
        if by_name[g]["availability"] != "VERIFIED":
            errors.append(_failure("FEATURE_AVAILABILITY_UNVERIFIED", g))
    if c["status"] != "PASS":
        errors.append(_failure("FEATURE_PROVENANCE_INCOMPLETE", "contract not verified"))
    temporal = c["temporal_scope"]
    if temporal.get("status") not in {"PASS", "NOT_APPLICABLE"}:
        errors.append(_failure("FUTURE_INFORMATION_LEAKAGE", "temporal gate not passed"))
    if temporal.get("status") == "NOT_APPLICABLE" and not temporal.get("rationale"):
        errors.append(_failure("FEATURE_PROVENANCE_INCOMPLETE", "justify static temporal scope"))
    if temporal.get("status") == "PASS":
        try:
            from .temporal_availability import temporal_scope_errors
        except ImportError:  # pragma: no cover
            from temporal_availability import temporal_scope_errors
        errors.extend(temporal_scope_errors(record.get("temporal_scope")))
        if record.get("temporal_scope", {}).get("temporal_gate_status") != "PASS":
            errors.append(_failure("FUTURE_INFORMATION_LEAKAGE", "independent temporal gate required"))
    for method, scope in ((c["selection_method"], c["selection_scope"]), (s["selection_method"], s["selection_scope"])):
        if (method == "NONE" and scope != "NONE") or (method != "NONE" and scope not in {"TRAIN_FOLD", "INNER_VALIDATION"}):
            errors.append(_failure("FEATURE_SELECTION_LEAKAGE", "learned selection must be training-fold/inner-validation only"))
    protocol = s["protocol"]
    if not isinstance(protocol, dict) or CONTROL_FIELDS - protocol.keys():
        return errors + [_failure("FEATURE_PROVENANCE_INCOMPLETE", "controlled protocol incomplete")]
    if protocol["model_family"] != s["model_family"]:
        errors.append(_failure("FEATURE_PROVENANCE_INCOMPLETE", "model family inconsistent"))
    if (c["selection_method"], c["selection_scope"]) != (s["selection_method"], s["selection_scope"]):
        errors.append(_failure("FEATURE_PROVENANCE_INCOMPLETE", "selection policy differs from contract"))
    metrics = set(protocol["metric_definitions"])
    for metric, definition in protocol["metric_definitions"].items():
        if not isinstance(definition, dict) or not isinstance(definition.get("higher_is_better"), bool) or not definition.get("definition"):
            errors.append(_failure("FEATURE_PROVENANCE_INCOMPLETE", f"metric definition/direction missing: {metric}"))
        elif metric in METRIC_DIRECTIONS and definition["higher_is_better"] != METRIC_DIRECTIONS[metric]:
            errors.append(f"METRIC_DIRECTION_ERROR: {metric}")
    if protocol["primary_metric"] not in metrics:
        errors.append(_failure("FEATURE_PROVENANCE_INCOMPLETE", "primary metric not reported"))
    if protocol["target_type"] == "ordinal" and (not ORDINAL_METRICS <= metrics or protocol["primary_metric"] == "Accuracy"):
        errors.append("ORDINAL_METRIC_GATE: retain distance-aware metrics and selection")
    if protocol.get("imbalanced") and (not IMBALANCE_METRICS <= metrics or protocol["primary_metric"] == "Accuracy"):
        errors.append("IMBALANCE_METRIC_GATE: accuracy cannot decide feature sets")
    sample_ids = s["sample_ids"]
    if not sample_ids or len(set(sample_ids)) != len(sample_ids) or len(protocol["target_values"]) != len(sample_ids):
        return errors + [_failure("FEATURE_PROVENANCE_INCOMPLETE", "unique sample IDs aligned with target required")]
    if not s["fold_ids"]:
        return errors + [_failure("FEATURE_PROVENANCE_INCOMPLETE", "actual fixed folds required")]
    group = c["group_scope"]
    entity_ids = s.get("entity_ids")
    if group.get("status") != "PASS" or (group.get("independence_required") and (not entity_ids or len(entity_ids) != len(sample_ids))):
        return errors + ["GROUP_SCOPE_UNVERIFIED: actual entity mapping required"]
    if c["prediction_setting"] in {"NEW_ENTITY", "NEW_ENTITY_FUTURE"} and not group.get("independence_required"):
        errors.append("GROUP_SCOPE_UNVERIFIED: new-entity setting requires entity separation")
    entities = dict(zip(sample_ids, entity_ids or sample_ids))
    seen_folds = set()
    fit_logs = s.get("fit_log", [])
    for fold in s["fold_ids"]:
        fid = fold.get("fold_id")
        train, valid = set(fold.get("train_ids", [])), set(fold.get("validation_ids", []))
        if (fid is None or fid in seen_folds or not train or not valid or train & valid or (train | valid) - set(sample_ids)
                or len(train) != len(fold["train_ids"]) or len(valid) != len(fold["validation_ids"])):
            errors.append("INVALID_SPLIT: missing/duplicate fold, overlap or unknown rows")
            continue
        seen_folds.add(fid)
        if group.get("independence_required") and {entities[i] for i in train} & {entities[i] for i in valid}:
            errors.append("GROUP_LEAKAGE: entity overlaps across fixed fold")
        logs = [f for f in fit_logs if f.get("fold_id") == fid]
        if record.get("status") == "OBSERVED" and not logs:
            errors.append(_failure("FEATURE_SELECTION_LEAKAGE", "missing actual pipeline fit IDs"))
        for log in logs:
            ids = set(log.get("fit_ids", []))
            if log.get("scope") != "TRAIN_FOLD" or not ids or ids - train or ids & valid:
                errors.append(_failure("FEATURE_SELECTION_LEAKAGE", "pipeline/selection fit uses non-training data"))
    if record.get("status") == "OBSERVED":
        measured = s.get("fold_metrics", [])
        if [f.get("fold_id") for f in measured] != [f["fold_id"] for f in s["fold_ids"]]:
            errors.append(_failure("FEATURE_PROVENANCE_INCOMPLETE", "measured fold IDs differ from planned fixed folds"))
        for f in measured:
            if not metrics <= f.get("metrics", {}).keys() or any(not np.isfinite(f["metrics"][m]) for m in metrics if m in f.get("metrics", {})):
                errors.append(_failure("FEATURE_PROVENANCE_INCOMPLETE", "all declared fold metrics must be finite and reported"))
    if any(f.get("fold_id") not in seen_folds for f in fit_logs):
        errors.append(_failure("FEATURE_PROVENANCE_INCOMPLETE", "fit log refers to an unknown fold"))
    design = c["comparison_protocol"]
    if design.get("design_source") == "FULL_DATA_TARGET_ASSOCIATION" and design.get("selection_validation") != "NESTED":
        errors.append(_failure("FEATURE_SELECTION_LEAKAGE", "outcome-driven group design outside validation"))
    if design.get("search_strategy") in {"POWERSET", "UNPLANNED_MANY"} and design.get("selection_validation") != "NESTED":
        errors.append(_failure("FEATURE_SET_SEARCH_OVERFIT_RISK", "unplanned combination search requires independent/nested evaluation"))
    if not design.get("rationale") or s["feature_set_id"] not in design.get("planned_candidates", []):
        errors.append(_failure("FEATURE_SET_SEARCH_OVERFIT_RISK", "candidate/order lacks a recorded rationale or prior plan"))
    return list(dict.fromkeys(errors))


def audit_feature_comparison(parent: dict, candidate: dict, *, contrast: str = "increment") -> dict:
    """Gate feature attribution before scoring; documented removal is not an increment."""
    errors = feature_set_errors(parent) + feature_set_errors(candidate)
    a, b = parent.get("feature_set", {}), candidate.get("feature_set", {})
    differences = []
    for key in ("sample_ids", "fold_ids", "entity_ids", "model_family", "selection_method", "selection_scope", "baseline_feature_set"):
        if a.get(key) != b.get(key):
            differences.append(key)
    pa, pb = a.get("protocol", {}), b.get("protocol", {})
    differences += [key for key in CONTROL_FIELDS if pa.get(key) != pb.get(key)]
    for key in ("baseline_feature_groups", "feature_groups", "comparison_protocol", "temporal_scope", "group_scope"):
        if parent.get("feature_set_contract", {}).get(key) != candidate.get("feature_set_contract", {}).get(key):
            differences.append(f"contract.{key}")
    if differences:
        errors.append(_failure("UNCONTROLLED_FEATURE_SET_COMPARISON", ", ".join(sorted(set(differences)))))
    if b.get("comparison_parent") != a.get("feature_set_id"):
        errors.append(_failure("FEATURE_PROVENANCE_INCOMPLETE", "comparison parent does not match"))
    ac, bc = set(a.get("feature_columns", [])), set(b.get("feature_columns", []))
    if contrast == "increment" and (not ac < bc):
        errors.append(_failure("UNCONTROLLED_FEATURE_SET_COMPARISON", "increment requires strict X -> X+G; baseline removed or no addition"))
    elif contrast == "drop" and not bc < ac:
        errors.append(_failure("UNCONTROLLED_FEATURE_SET_COMPARISON", "drop requires strict Full -> Full-G"))
    elif contrast not in {"increment", "drop", "composition_diagnostic"}:
        raise ValueError("unknown contrast")
    return {"status": "FAIL" if errors else "PASS", "errors": list(dict.fromkeys(errors)),
            "contrast": contrast, "changed_controls": sorted(set(differences)),
            "sample_composition_change": a.get("sample_ids") != b.get("sample_ids"),
            "added_columns": sorted(bc - ac), "removed_columns": sorted(ac - bc)}


def paired_metric_summary(parent: list[dict], candidate: list[dict], *, metric: str,
                          higher_is_better: bool, practical_delta: float,
                          minimum_consistency: float = .75, contrast: str = "increment") -> dict:
    """Describe dependent CV fold deltas; no p-value, confidence interval or guarantee.

    practical_delta and consistency must be set before seeing results. A conservative
    descriptive label requires a positive median and a mean exceeding both that
    threshold and the fold-delta standard deviation. Repeated folds are dependent.
    """
    if practical_delta < 0 or not .5 <= minimum_consistency <= 1:
        raise ValueError("invalid predeclared evidence thresholds")
    if metric in METRIC_DIRECTIONS and higher_is_better != METRIC_DIRECTIONS[metric]:
        raise ValueError(f"METRIC_DIRECTION_ERROR: {metric}")
    if contrast not in {"increment", "drop", "composition_diagnostic"}:
        raise ValueError("unknown contrast")
    if [f["fold_id"] for f in parent] != [f["fold_id"] for f in candidate] or len({f["fold_id"] for f in parent}) != len(parent):
        raise ValueError("UNCONTROLLED_FEATURE_SET_COMPARISON: paired fold IDs must match uniquely")
    x = np.asarray([f["metrics"][metric] for f in parent], float)
    y = np.asarray([f["metrics"][metric] for f in candidate], float)
    if len(x) < 2 or not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError("at least two finite paired metrics required; do not omit failed folds")
    delta = y - x
    oriented = delta * (1 if higher_is_better else -1) * (-1 if contrast == "drop" else 1)
    mean, median, std = float(oriented.mean()), float(np.median(oriented)), float(oriented.std(ddof=1))
    consistency = float(np.mean(oriented > 0))
    supported = mean > max(practical_delta, std) and median > 0 and consistency >= minimum_consistency
    label = ("SUPPORTED_CONTRIBUTION" if contrast == "drop" else "SUPPORTED_INCREMENTAL_VALUE") if supported else "NO_CLEAR_INCREMENTAL_VALUE"
    if contrast == "composition_diagnostic":
        label = "COMPOSITION_DIAGNOSTIC_ONLY"
    return {"metric": metric, "higher_is_better": higher_is_better, "contrast": contrast,
            "parent_mean": float(x.mean()), "candidate_mean": float(y.mean()),
            "raw_deltas": delta.tolist(), "mean_delta": float(delta.mean()), "median_delta": float(np.median(delta)),
            "benefit_deltas": oriented.tolist(), "mean_benefit": mean, "median_benefit": median,
            "delta_std": std, "sign_consistency": consistency, "practical_delta": practical_delta,
            "minimum_consistency": minimum_consistency, "status": label,
            "uncertainty_note": "descriptive paired folds, not independent replications or a confidence interval"}


def apply_feature_set_gate(record: dict) -> dict:
    result = deepcopy(record)
    errors = feature_set_errors(result)
    result["feature_set_gate"] = {"status": "FAIL" if errors else "PASS", "errors": errors}
    if errors:
        result["status"] = "INVALIDATED"
        result["invalidation_reason"] = "; ".join(filter(None, [result.get("invalidation_reason"), *errors]))
    return result


def review_feature_claim(text: str, *, candidate: dict, parent: dict | None = None,
                         contrast: str = "increment", paired_evidence: dict | None = None) -> dict:
    """Audit the evidence, not just keywords; ambiguous prose still needs human review."""
    findings = feature_set_errors(candidate)
    gain_claim = False
    for clause in re.split(r"[。；;.!?]|\bbut\b|但是|但", text, flags=re.I):
        match = re.search(r"(提高|提升|改善|增益|贡献|improv|benefit|contribut)", clause, re.I)
        if match and not re.search(r"(未|没有|无明确|不能|尚不|不支持|\bno\b|\bnot\b|\bwithout\b)", clause[:match.start()], re.I):
            gain_claim = True
    if gain_claim:
        if candidate.get("status") != "OBSERVED" or (parent is not None and parent.get("status") != "OBSERVED"):
            findings.append("UNSUPPORTED_FEATURE_BENEFIT_CLAIM: completed observed experiments required")
        if parent is None:
            findings.append("UNCONTROLLED_FEATURE_SET_COMPARISON: improvement requires a controlled parent experiment")
        else:
            findings.extend(audit_feature_comparison(parent, candidate, contrast=contrast)["errors"])
        expected = "SUPPORTED_CONTRIBUTION" if contrast == "drop" else "SUPPORTED_INCREMENTAL_VALUE"
        if not paired_evidence or paired_evidence.get("status") != expected or contrast == "composition_diagnostic":
            findings.append("UNSUPPORTED_FEATURE_BENEFIT_CLAIM: evidence supports use, not established improvement")
        elif parent is not None:
            try:
                protocol = candidate["feature_set"]["protocol"]
                metric = protocol["primary_metric"]
                policy = candidate["feature_set_contract"]["comparison_protocol"]
                computed = paired_metric_summary(parent["feature_set"]["fold_metrics"], candidate["feature_set"]["fold_metrics"],
                    metric=metric, higher_is_better=protocol["metric_definitions"][metric]["higher_is_better"],
                    practical_delta=policy["practical_deltas"][metric],
                    minimum_consistency=policy["minimum_consistency"], contrast=contrast)
                if computed != paired_evidence or computed["status"] != expected:
                    findings.append("UNSUPPORTED_FEATURE_BENEFIT_CLAIM: paired evidence does not match actual folds and predeclared policy")
            except (KeyError, TypeError, ValueError):
                findings.append("UNSUPPORTED_FEATURE_BENEFIT_CLAIM: actual paired metrics and predeclared policy required")
    return {"status": "FAIL" if findings else "PASS", "findings": list(dict.fromkeys(findings))}
