"""Small, explicit guards and linear models for observational associations.

These helpers audit declared variable roles; column names cannot prove timing
or randomization. They do not identify causal effects or select confounders.
"""

from __future__ import annotations

import copy
from collections.abc import Mapping, Sequence
import re
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import t as student_t

try:
    from .group_validation import group_structure_contract
    from .temporal_availability import validate_temporal_availability
except ImportError:  # pragma: no cover - standalone Skill directory
    from group_validation import group_structure_contract
    from temporal_availability import validate_temporal_availability


class AssociationAnalysisError(ValueError):
    """An invalid analysis/claim, not a warning to ignore after fitting."""


ASSIGNMENT_TYPES = {"RANDOMIZED", "OBSERVATIONAL", "UNKNOWN"}
CLAIM_LEVELS = {"DESCRIPTIVE_ASSOCIATION", "ADJUSTED_ASSOCIATION", "CAUSAL_EFFECT"}
DEPENDENCE_METHODS = {"ENTITY_CLUSTERED", "GEE", "MIXED_MODEL", "ENTITY_SUMMARY"}
CONTRACT_FIELDS = {
    "exposure", "outcome", "assignment_type", "exposure_time_known",
    "candidate_confounders", "post_exposure_variables", "group_structure",
    "temporal_structure", "estimand", "claim_level",
}


def _names(value: str | Sequence[str]) -> list[str]:
    names = [value] if isinstance(value, str) else list(value)
    if not names or any(not isinstance(name, str) or not name.strip() for name in names):
        raise AssociationAnalysisError("VARIABLE_ROLE_UNVERIFIED: non-empty variable names required")
    if len(set(names)) != len(names):
        raise AssociationAnalysisError("duplicate variable names")
    return names


def build_association_contract(
    *, exposure: str | Sequence[str], outcome: str, assignment_type: str = "UNKNOWN",
    exposure_time_known: bool = False, candidate_confounders: Sequence[Mapping] = (),
    post_exposure_variables: Sequence[str] = (), group_structure: Mapping,
    temporal_structure: Mapping, estimand: str,
    claim_level: str = "DESCRIPTIVE_ASSOCIATION", joint_variables: Sequence[Mapping] = (),
    causal_identification: Mapping | None = None,
) -> dict[str, Any]:
    """Build the auditable contract without promoting associations to causes.

    A confounder entry needs name, temporal_role=PRE_EXPOSURE and evidence.
    Optional available_at/exposure_at values are checked by the Temporal Gate.
    Joint variables are separately declared descriptive study variables, never
    an escape hatch for labeling post-exposure measurements as confounders.
    """
    contract = {
        "exposure": _names(exposure), "outcome": outcome,
        "assignment_type": assignment_type, "exposure_time_known": exposure_time_known,
        "candidate_confounders": [dict(item) for item in candidate_confounders],
        "post_exposure_variables": list(post_exposure_variables),
        "group_structure": dict(group_structure), "temporal_structure": dict(temporal_structure),
        "estimand": estimand, "claim_level": claim_level,
        "joint_variables": [dict(item) for item in joint_variables],
        "causal_identification": dict(causal_identification or {}),
    }
    audit = validate_association_contract(contract)
    return {**contract, **audit}


def _causal_support(contract: Mapping) -> bool:
    identification = contract.get("causal_identification", {})
    # This is evidence of a separate design review, not an identification
    # procedure. A fitted regression, balance table or matching call is not one.
    return bool(
        contract.get("exposure_time_known") is True
        and contract.get("assignment_type") in {"RANDOMIZED", "OBSERVATIONAL"}
        and isinstance(identification, Mapping)
        and identification.get("review_status") == "VERIFIED"
        and identification.get("strategy")
        and identification.get("evidence_refs")
        and identification.get("assumptions")
        and identification.get("temporal_order_verified") is True
        and identification.get("strategy") == (
            "RANDOMIZED_ASSIGNMENT" if contract.get("assignment_type") == "RANDOMIZED"
            else "EXTERNALLY_IDENTIFIED_DESIGN")
        and (contract.get("assignment_type") != "RANDOMIZED"
             or identification.get("randomization_verified") is True)
        and not contract.get("joint_variables")
    )


def _confounder_errors(contract: Mapping, variables: Sequence[str], *, propensity: bool = False) -> list[str]:
    metadata = {item.get("name"): item for item in contract.get("candidate_confounders", [])}
    forbidden = set(contract.get("post_exposure_variables", [])) | {contract.get("outcome")}
    exposures = set(_names(contract["exposure"]))
    errors = []
    for name in variables:
        item = metadata.get(name, {})
        if (name == contract.get("outcome") or item.get("source_role") == "OUTCOME"
                or contract.get("outcome") in item.get("derived_from", [])):
            errors.append(f"OUTCOME_LEAKAGE: {name} cannot enter adjustment or a propensity model")
        elif name in exposures:
            errors.append(f"EXPOSURE_ROLE_CONFLICT: {name} is not a confounder")
        elif name in forbidden or item.get("temporal_role") == "POST_EXPOSURE":
            errors.append(f"POST_EXPOSURE_ADJUSTMENT: {name} is not an ordinary confounder")
        elif item.get("temporal_role") != "PRE_EXPOSURE" or not item.get("evidence"):
            errors.append(f"CONFOUNDER_TIME_UNVERIFIED: {name} needs pre-exposure evidence")
        if "available_at" in item or "exposure_at" in item:
            timing = validate_temporal_availability(
                [item.get("available_at")], cutoff=item.get("exposure_at"), aggregation_required=True,
            )
            if timing["status"] != "PASS":
                errors.append(f"CONFOUNDER_TIME_UNVERIFIED: {name} has unverified timestamps")
            elif timing["post_horizon_records"]:
                errors.append(f"FUTURE_INFORMATION_LEAKAGE: {name} became available after exposure")
    if propensity and not variables:
        errors.append("PROPENSITY_COVARIATES_UNVERIFIED: declare the actual treatment-model inputs")
    return errors


def validate_association_contract(
    contract: Mapping, *, adjustment_variables: Sequence[str] = (),
    propensity_features: Sequence[str] | None = None, dependence_handling: str | None = None,
) -> dict[str, Any]:
    """Recompute all gates; do not trust a saved status/claim-level label."""
    if not isinstance(contract, Mapping):
        return {"status": "FAIL", "errors": ["ASSOCIATION_CONTRACT_REQUIRED"], "warnings": []}
    errors = [f"ASSOCIATION_CONTRACT_MISSING: {name}" for name in sorted(CONTRACT_FIELDS - contract.keys())]
    warnings = []
    if errors:
        return {"status": "FAIL", "errors": errors, "warnings": warnings}
    for field in ("candidate_confounders", "joint_variables"):
        entries = contract.get(field, [])
        if not isinstance(entries, (list, tuple)) or any(not isinstance(item, Mapping) for item in entries):
            return {"status": "FAIL", "errors": [f"{field} must contain variable metadata mappings"], "warnings": []}
        names = [item.get("name") for item in entries]
        if any(not isinstance(name, str) or not name for name in names) or len(set(names)) != len(names):
            return {"status": "FAIL", "errors": [f"{field} requires unique, non-empty names"], "warnings": []}
    post_variables = contract.get("post_exposure_variables")
    if not isinstance(post_variables, (list, tuple)) or any(not isinstance(name, str) for name in post_variables):
        return {"status": "FAIL", "errors": ["post_exposure_variables must be a list of names"], "warnings": []}
    if contract["assignment_type"] not in ASSIGNMENT_TYPES:
        errors.append("ASSIGNMENT_TYPE_UNVERIFIED")
    if contract["claim_level"] not in CLAIM_LEVELS:
        errors.append("CLAIM_LEVEL_UNVERIFIED")
    if type(contract["exposure_time_known"]) is not bool:
        errors.append("EXPOSURE_TIME_UNVERIFIED: use an explicit Boolean, not a truthy string")
    if contract["exposure_time_known"] is not True:
        warnings.append("EXPOSURE_TIME_UNVERIFIED")
    if contract["assignment_type"] != "RANDOMIZED":
        warnings.append("CONFOUNDING_BY_INDICATION: assignment may depend on baseline risk/need")
    if not contract.get("estimand") or not contract.get("outcome"):
        errors.append("ASSOCIATION_TARGET_UNVERIFIED")
    try:
        exposures = _names(contract["exposure"])
        if contract["outcome"] in exposures:
            errors.append("OUTCOME_LEAKAGE: exposure and outcome must differ")
    except (TypeError, ValueError) as exc:
        return {"status": "FAIL", "errors": [str(exc)], "warnings": warnings}
    allowed = ["DESCRIPTIVE_ASSOCIATION", "ADJUSTED_ASSOCIATION"]
    if _causal_support(contract):
        allowed.append("CAUSAL_EFFECT")
    if contract["claim_level"] == "CAUSAL_EFFECT" and "CAUSAL_EFFECT" not in allowed:
        errors.append("UNSUPPORTED_CAUSAL_CLAIM: no verified identification and temporal order")
    temporal = contract["temporal_structure"]
    if (not isinstance(temporal, Mapping) or temporal.get("status") != "PASS"
            or temporal.get("purpose") not in {"RETROSPECTIVE_ASSOCIATION", "PROSPECTIVE_ANALYSIS", "STATIC_ASSOCIATION"}
            or not temporal.get("evidence")):
        errors.append("TEMPORAL_STRUCTURE_UNVERIFIED")
    elif temporal.get("future_information_used") or temporal.get("post_horizon_records_used", 0):
        errors.append("FUTURE_INFORMATION_LEAKAGE: association does not waive the Temporal Gate")
    group = contract["group_structure"]
    if not isinstance(group, Mapping) or group.get("status") != "PASS":
        errors.append("GROUP_STRUCTURE_UNVERIFIED")
    elif group.get("repeated_entities"):
        if dependence_handling is not None and dependence_handling not in DEPENDENCE_METHODS:
            errors.append("PSEUDOREPLICATION: repeated rows require entity dependence handling")
        if not group.get("entity_key"):
            errors.append("GROUP_KEY_MISSING")
    errors.extend(_confounder_errors(contract, adjustment_variables))
    if propensity_features is not None:
        errors.extend(_confounder_errors(contract, propensity_features, propensity=True))
    for item in contract.get("joint_variables", []):
        if (not item.get("name") or item.get("role") != "JOINT_ASSOCIATION_VARIABLE"
                or not item.get("evidence") or item.get("availability") != "AT_OR_BEFORE_OUTCOME"):
            errors.append("JOINT_VARIABLE_UNVERIFIED: document the study role and outcome-time availability")
        if item.get("name") == contract.get("outcome"):
            errors.append("OUTCOME_LEAKAGE: outcome cannot also be a joint explanatory variable")
        if item.get("name") in adjustment_variables:
            errors.append("POST_EXPOSURE_ADJUSTMENT: joint study variables cannot masquerade as confounders")
    if contract.get("joint_variables"):
        warnings.append("JOINT_CONDITIONING_ONLY: joint variables are not verified pre-exposure confounders")
    return {"status": "FAIL" if errors else "PASS", "errors": list(dict.fromkeys(errors)),
            "warnings": list(dict.fromkeys(warnings)), "allowed_claim_levels": allowed}


def require_association_contract(contract: Mapping, **kwargs) -> dict[str, Any]:
    report = validate_association_contract(contract, **kwargs)
    if report["errors"]:
        raise AssociationAnalysisError("; ".join(report["errors"]))
    return report


def _entity_table(data: pd.DataFrame, columns: Sequence[str], entity_key: str | None) -> pd.DataFrame:
    frame = data[list(dict.fromkeys(([entity_key] if entity_key else []) + list(columns)))].copy()
    if entity_key:
        if frame[entity_key].isna().any() or frame[entity_key].astype(str).str.strip().eq("").any():
            raise AssociationAnalysisError("GROUP_KEY_MISSING")
        if (frame.groupby(entity_key)[list(columns)].nunique(dropna=False) > 1).any().any():
            raise AssociationAnalysisError("TIME_VARYING_EXPOSURE_OR_BASELINE: define a time-varying analysis explicitly")
        frame = frame.drop_duplicates(entity_key)
    return frame


def _summary(values: pd.Series) -> dict[str, Any]:
    values = pd.to_numeric(values, errors="raise").dropna()
    return {"n": int(len(values)), "mean": float(values.mean()) if len(values) else None,
            "median": float(values.median()) if len(values) else None,
            "std": float(values.std(ddof=1)) if len(values) > 1 else None}


def _smd(x0, x1, *, mean0=None, mean1=None) -> float | None:
    a, b = np.asarray(x0, float), np.asarray(x1, float)
    a, b = a[np.isfinite(a)], b[np.isfinite(b)]
    if len(a) < 2 or len(b) < 2:
        return None
    scale = float(np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2))
    difference = float((b.mean() if mean1 is None else mean1) - (a.mean() if mean0 is None else mean0))
    return difference / scale if scale > 0 else 0.0 if difference == 0 else None


def audit_exposures(
    data: pd.DataFrame, exposures: Sequence[str], *, outcome: str,
    baseline_variables: Sequence[str] = (), entity_key: str | None = None,
    min_arm_entities: int = 10, high_correlation: float = .85,
) -> dict[str, Any]:
    """Count entities, including missing exposure; never recode missing as 0.

    Repeated outcomes are summarized as one observed mean per entity. Initial
    measurements may be described here without being approved for adjustment.
    """
    exposures = _names(exposures)
    if min_arm_entities < 1 or not 0 < high_correlation <= 1:
        raise ValueError("invalid exposure support thresholds")
    entities = _entity_table(data, [*exposures, *baseline_variables], entity_key)
    if entity_key:
        outcomes = data.groupby(entity_key)[outcome].mean()
        entities[outcome] = entities[entity_key].map(outcomes)
    else:
        entities[outcome] = data[outcome]
    for name in [*exposures, *baseline_variables, outcome]:
        entities[name] = pd.to_numeric(entities[name], errors="raise")
        if np.isinf(entities[name].to_numpy(float)).any():
            raise AssociationAnalysisError("non-finite analysis values")
    audit = {}
    for name in exposures:
        if not set(entities[name].dropna().unique()) <= {0, 1}:
            raise AssociationAnalysisError(f"BINARY_EXPOSURE_REQUIRED: {name}")
        absent, present = entities[entities[name] == 0], entities[entities[name] == 1]
        n0, n1 = len(absent), len(present)
        audit[name] = {
            "untreated_n": n0, "treated_n": n1, "missing_exposure_n": int(entities[name].isna().sum()),
            "prevalence": n1 / (n0 + n1) if n0 + n1 else None,
            "status": "ESTIMATE_UNSTABLE" if min(n0, n1) < min_arm_entities else "SUPPORTED_FOR_EXPLORATION",
            "outcome": {"untreated": _summary(absent[outcome]), "treated": _summary(present[outcome])},
            "baseline": {variable: {"untreated": _summary(absent[variable]), "treated": _summary(present[variable]),
                                    "standardized_mean_difference": _smd(absent[variable], present[variable])}
                         for variable in baseline_variables},
        }
    pairs = []
    for i, left in enumerate(exposures):
        for right in exposures[i + 1:]:
            pair = entities[[left, right]].dropna()
            phi = float(pair[left].corr(pair[right])) if pair[left].nunique() > 1 and pair[right].nunique() > 1 else None
            pairs.append({"left": left, "right": right, "complete_entity_n": len(pair),
                          "both_exposed_n": int(((pair[left] == 1) & (pair[right] == 1)).sum()),
                          "phi": phi, "highly_correlated": phi is not None and abs(phi) >= high_correlation})
    return {"unit_of_analysis": "ENTITY" if entity_key else "ROW", "n_entities": len(entities),
            "n_rows": len(data), "outcome_summary_unit": "ENTITY_OBSERVED_MEAN" if entity_key else "ROW",
            "min_arm_entities": min_arm_entities, "exposures": audit, "cooccurrence": pairs}


def _clustered_linear(design: pd.DataFrame, outcome: np.ndarray, groups: np.ndarray, *, independent_rows=False) -> dict[str, Any]:
    """Equal-entity WLS with CR1 cluster sandwich and t(G-1) intervals."""
    codes, unique = pd.factorize(groups, sort=False)
    n, p, g = len(outcome), design.shape[1], len(unique)
    if g <= max(p, 2) or n <= p:
        raise AssociationAnalysisError("INSUFFICIENT_INDEPENDENT_ENTITIES: reduce model dimension")
    x = design.to_numpy(float)
    weights = 1 / np.bincount(codes)[codes]
    xw = x * np.sqrt(weights)[:, None]
    if np.linalg.matrix_rank(xw) != p:
        raise AssociationAnalysisError("ASSOCIATION_MODEL_NOT_IDENTIFIED: rank-deficient design")
    beta = np.linalg.lstsq(xw, outcome * np.sqrt(weights), rcond=None)[0]
    residual = outcome - x @ beta
    bread = np.linalg.inv(xw.T @ xw)
    scores = np.zeros((g, p))
    np.add.at(scores, codes, x * (weights * residual)[:, None])
    covariance = (g / (g - 1)) * ((n - 1) / (n - p)) * bread @ (scores.T @ scores) @ bread
    se = np.sqrt(np.maximum(np.diag(covariance), 0))
    df = n - p if independent_rows else g - 1
    critical = float(student_t.ppf(.975, df))
    coefficients = {name: {"estimate": float(beta[i]), "se": float(se[i]),
                           "ci95": [float(beta[i] - critical * se[i]), float(beta[i] + critical * se[i])]}
                    for i, name in enumerate(design.columns)}
    return {"coefficients": coefficients, "n_rows": n, "n_entities": g, "n_parameters": p,
            "uncertainty_unit": "ROW" if independent_rows else "ENTITY",
            "covariance": "HC1" if independent_rows else "CR1_CLUSTER_SANDWICH", "df": df,
            "interval_scope": "nominal, model-conditional; exploratory, not simultaneous across exposures",
            "weighting": "each independent row has weight one" if independent_rows else "each entity has total weight one",
            "condition_number": float(np.linalg.cond(xw)),
            "fit_residual_scope": "FIT_RESIDUAL", "predictive_validation_performed": False}


def fit_crude_adjusted_association(
    data: pd.DataFrame, contract: Mapping, *, adjustment_variables: Sequence[str],
    time_column: str | None = None, quadratic_time: bool = False, time_interaction: bool = False,
) -> dict[str, Any]:
    """Prespecified linear association, same complete-case rows in both models.

    Time is a documented coordinate, not time-since-exposure unless verified.
    No propensity fitting, model search, automatic imputation or validation
    score is hidden here. A predictive use still needs separate grouped CV.
    """
    gate = require_association_contract(contract, adjustment_variables=adjustment_variables,
                                        dependence_handling="ENTITY_CLUSTERED")
    adjustment_variables = _names(adjustment_variables)
    if not data.index.is_unique:
        raise AssociationAnalysisError("ANALYSIS_ROW_IDS_NOT_UNIQUE")
    exposures = _names(contract["exposure"])
    joint = [item["name"] for item in contract.get("joint_variables", [])]
    key = contract["group_structure"].get("entity_key")
    if key:
        actual = group_structure_contract(data, entity_key=key, validation_unit="ENTITY")
        for field in ("n_rows", "n_entities", "repeated_entities"):
            if actual[field] != contract["group_structure"].get(field):
                raise AssociationAnalysisError(f"GROUP_STRUCTURE_MISMATCH: {field}")
    elif contract["group_structure"].get("repeated_entities"):
        raise AssociationAnalysisError("GROUP_KEY_MISSING")
    _entity_table(data, [*exposures, *adjustment_variables], key)
    if (quadratic_time or time_interaction) and time_column is None:
        raise AssociationAnalysisError("trajectory terms require a time coordinate")
    columns = list(dict.fromkeys([contract["outcome"], *exposures, *joint, *adjustment_variables]
                                + ([time_column] if time_column else [])))
    if contract["outcome"] in [*exposures, *joint, *adjustment_variables, time_column]:
        raise AssociationAnalysisError("OUTCOME_LEAKAGE")
    numeric = data[columns].apply(pd.to_numeric, errors="raise")
    if np.isinf(numeric.to_numpy(float)).any():
        raise AssociationAnalysisError("non-finite analysis values")
    keep = numeric.notna().all(axis=1)
    frame = numeric.loc[keep]
    ids = data.loc[keep, key].to_numpy() if key else np.arange(len(frame))
    if key and pd.isna(ids).any():
        raise AssociationAnalysisError("GROUP_KEY_MISSING")
    if any(not set(frame[name].unique()) <= {0, 1} for name in exposures):
        raise AssociationAnalysisError("BINARY_EXPOSURE_REQUIRED: define another contrast explicitly")
    for name in exposures:
        if frame[name].nunique() < 2:
            raise AssociationAnalysisError(f"EXPOSURE_CONTRAST_UNIDENTIFIED: {name}")
    design = pd.DataFrame({"intercept": np.ones(len(frame))}, index=frame.index)
    if time_column:
        design[time_column] = frame[time_column]
        if quadratic_time:
            design[time_column + "^2"] = frame[time_column] ** 2
    for name in [*exposures, *joint]:
        design[name] = frame[name]
    if time_interaction:
        for name in exposures:
            design[name + ":" + time_column] = frame[name] * frame[time_column]
    crude = _clustered_linear(design, frame[contract["outcome"]].to_numpy(float), ids, independent_rows=key is None)
    adjusted_design = design.copy()
    for name in adjustment_variables:
        if name in adjusted_design:
            raise AssociationAnalysisError("DUPLICATE_MODEL_ROLE")
        adjusted_design[name] = frame[name]
    adjusted = _clustered_linear(adjusted_design, frame[contract["outcome"]].to_numpy(float), ids, independent_rows=key is None)
    support_frame = data.loc[keep].copy()
    support = audit_exposures(support_frame, exposures, outcome=contract["outcome"], entity_key=key)
    warnings = gate["warnings"] + ["ESTIMATE_UNSTABLE: " + name for name, item in support["exposures"].items()
                                    if item["status"] == "ESTIMATE_UNSTABLE"]
    if max(crude["condition_number"], adjusted["condition_number"]) > 1e8:
        warnings.append("ESTIMATE_UNSTABLE: high design condition number")
    comparisons = {}
    for name in [*exposures, *([name + ":" + time_column for name in exposures] if time_interaction else []), *joint]:
        before, after = crude["coefficients"][name]["estimate"], adjusted["coefficients"][name]["estimate"]
        comparisons[name] = {"crude": before, "adjusted": after, "change": after - before,
                             "interpretation": "a change may reflect confounding/specification; neither estimate identifies an effect"}
    scope = {"claim_level": contract["claim_level"], "adjustment_variables": list(adjustment_variables),
             "dependence_handling": "ENTITY_CLUSTERED", "analyzed_entity_ids": ids.tolist(),
             "n_rows": len(frame), "n_entities": int(pd.Series(ids).nunique()),
             "fit_row_ids": frame.index.tolist(), "dropped_row_ids": data.index[~keep].tolist()}
    return {"status": "OBSERVED", "claim_level": contract["claim_level"], "scope": scope,
            "crude": crude, "adjusted": adjusted, "comparison": comparisons, "support": support,
            "warnings": warnings, "time_interaction_interpretation": "TRAJECTORY_ASSOCIATION" if time_interaction else None,
            "causal_identification_established_by_model": False}


def propensity_diagnostics(
    data: pd.DataFrame, contract: Mapping, probabilities: Sequence[float], *,
    covariates: Sequence[str], weights: Sequence[float] | None = None,
    extreme_weight: float = 10, min_effective_size: float = 10,
) -> dict[str, Any]:
    """Optional binary propensity checks, on one verified row per entity.

    Covariates must name the actual treatment-model inputs, not just a chosen
    balance subset; supplied scores cannot reveal their own fitting provenance.
    Does not fit a propensity model, clip weights, match, or confer causality.
    Balance uses the same unweighted pooled SD before and after weighting.
    """
    require_association_contract(contract, propensity_features=covariates)
    exposures = _names(contract["exposure"])
    if len(exposures) != 1:
        raise AssociationAnalysisError("define a single binary propensity contrast")
    key = contract["group_structure"].get("entity_key")
    if key and (data[key].isna().any() or data[key].duplicated().any()):
        raise AssociationAnalysisError("PROPENSITY_UNIT_ERROR: use one verified row per entity")
    z = data[exposures[0]].to_numpy(float)
    p = np.asarray(probabilities, dtype=float)
    x = data[list(covariates)].to_numpy(float)
    if p.shape != z.shape or not np.isfinite(p).all() or not np.isfinite(x).all() or set(z) != {0, 1}:
        raise AssociationAnalysisError("invalid propensity inputs or missing exposure contrast")
    if np.any((p < 0) | (p > 1)):
        raise AssociationAnalysisError("propensity probabilities must be in [0, 1]")
    errors, warnings = [], []
    if np.any((p == 0) | (p == 1)):
        return {"status": "FAIL", "errors": ["POSITIVITY_FAILURE"], "warnings": [],
                "eligible_for_weighted_association": False, "causal_identification_established": False}
    p0, p1 = p[z == 0], p[z == 1]
    lower, upper = max(p0.min(), p1.min()), min(p0.max(), p1.max())
    in_support = (p >= lower) & (p <= upper)
    if lower > upper or not all(np.any(in_support & (z == level)) for level in (0, 1)):
        errors.append("PROPENSITY_OVERLAP_FAILURE")
    elif any(np.mean(in_support[z == level]) < .5 for level in (0, 1)):
        warnings.append("LIMITED_PROPENSITY_OVERLAP")
    w = z / p + (1 - z) / (1 - p) if weights is None else np.asarray(weights, dtype=float)
    if w.shape != z.shape or not np.isfinite(w).all() or np.any(w <= 0):
        raise AssociationAnalysisError("weights must be positive, finite, and aligned")
    ess = lambda values: float(values.sum() ** 2 / (values @ values))
    effective = {"total": ess(w), "untreated": ess(w[z == 0]), "treated": ess(w[z == 1])}
    if np.any(w > extreme_weight):
        warnings.append("EXTREME_IPTW_WEIGHTS")
    if min(effective["untreated"], effective["treated"]) < min_effective_size:
        warnings.append("LOW_EFFECTIVE_SAMPLE_SIZE")
    balance = {}
    for i, name in enumerate(covariates):
        a, b = x[z == 0, i], x[z == 1, i]
        balance[name] = {"before_smd": _smd(a, b),
                         "after_smd": _smd(a, b, mean0=float(np.average(a, weights=w[z == 0])),
                                           mean1=float(np.average(b, weights=w[z == 1])))}
    if any(item["after_smd"] is None or abs(item["after_smd"]) > .1 for item in balance.values()):
        warnings.append("RESIDUAL_COVARIATE_IMBALANCE")
    return {"status": "FAIL" if errors else "PASS_WITH_WARNINGS" if warnings else "PASS",
            "errors": errors, "warnings": warnings, "common_support": [float(lower), float(upper)],
            "support_fraction_by_arm": {str(level): float(np.mean(in_support[z == level])) for level in (0, 1)},
            "max_weight": float(w.max()), "extreme_weight_count": int((w > extreme_weight).sum()),
            "effective_sample_size": effective, "balance": balance,
            "eligible_for_weighted_association": not errors and not warnings,
            "causal_identification_established": False}


def review_association_claim(text: str, contract: Mapping) -> dict[str, Any]:
    """Catch common causal language; semantic review of the full text remains necessary."""
    audit = validate_association_contract(contract)
    if not isinstance(contract, Mapping) or not contract.get("exposure"):
        return {"status": "INVALIDATED", "findings": [{"code": "ASSOCIATION_CONTRACT_INVALID", "severity": "P1",
                                                         "text": "provide the audited assignment and exposure definition"}]}
    findings = []
    unsupported = bool(audit["errors"]) or "CAUSAL_EFFECT" not in audit.get("allowed_claim_levels", [])
    subjects = r"treatment|intervention|policy|action|exposure|" + "|".join(
        re.escape(name) for name in _names(contract["exposure"]))
    causal = re.compile(
        r"导致|使得|有效(?:降低|减少|增加|改善|提升)|(?:该|此)?(?:治疗|干预|政策|措施)(?:增加|降低|减少)风险"
        r"|\bcaus(?:e[sd]?|ing|al\s+effect)\b|\beffective(?:ly)?\s+(?:in\s+)?(?:reduc\w*|lower\w*)"
        rf"|\b(?:{subjects})\s+(?:reduces?|increases?|improves?|prevents?|lowers?|raises?)\b",
        re.IGNORECASE,
    )
    negation = re.compile(r"(?:不能|无法|未能|没有证据|不应|并非).{0,16}(?:证明|推断|认定|说明|声称|因果)|"
                          r"(?:cannot|can't|does not|no evidence|not an?).{0,35}(?:conclud|infer|establish|show|causal)", re.I)
    for clause in re.split(r"[。；;!！?？\n，,]|(?<!\d)\.(?!\d)", text):
        if unsupported and causal.search(clause) and not negation.search(clause):
            findings.append({"code": "UNSUPPORTED_CAUSAL_CLAIM", "severity": "P1", "text": clause.strip()})
    if any("UNSUPPORTED_CAUSAL_CLAIM" in error for error in audit["errors"]):
        findings.append({"code": "UNSUPPORTED_CAUSAL_CLAIM", "severity": "P1", "text": "contract claim_level"})
    return {"status": "INVALIDATED" if findings else "PASS", "findings": findings,
            "scope": "common causal wording plus structured claim level; not exhaustive semantic review"}


def association_scope_errors(contract: Mapping, scope: Mapping) -> list[str]:
    """Recheck an experiment's actual adjustment and independent analysis units."""
    if not isinstance(contract, Mapping) or not isinstance(scope, Mapping):
        return ["association_contract and association_scope are required"]
    audited = dict(contract)
    audited["claim_level"] = scope.get("claim_level", contract.get("claim_level"))
    report = validate_association_contract(
        audited, adjustment_variables=scope.get("adjustment_variables", []),
        propensity_features=scope.get("propensity_features"), dependence_handling=scope.get("dependence_handling"),
    )
    errors = report["errors"][:]
    if scope.get("claim_level") != contract.get("claim_level"):
        errors.append("ASSOCIATION_CLAIM_LEVEL_MISMATCH")
    group = contract.get("group_structure", {})
    if not isinstance(group, Mapping):
        return errors
    ids = scope.get("analyzed_entity_ids", [])
    if not isinstance(ids, list) or not ids or any(not np.isscalar(value) for value in ids):
        return errors + ["ASSOCIATION_ENTITY_PROVENANCE_REQUIRED"]
    if pd.Series(ids).isna().any() or any(isinstance(value, str) and not value.strip() for value in ids):
        errors.append("ASSOCIATION_ENTITY_PROVENANCE_REQUIRED")
    elif scope.get("n_rows") != len(ids) or scope.get("n_entities") != pd.Series(ids).nunique():
        errors.append("PSEUDOREPLICATION: entity counts disagree with actual analysis IDs")
    elif group.get("n_entities") is not None and scope["n_entities"] > group["n_entities"]:
        errors.append("PSEUDOREPLICATION: cannot substitute row IDs for independent entities")
    if group.get("repeated_entities") and scope.get("dependence_handling") not in DEPENDENCE_METHODS:
        errors.append("PSEUDOREPLICATION: no entity dependence handling")
    if scope.get("dependence_handling") == "ENTITY_SUMMARY" and len(ids) != pd.Series(ids).nunique():
        errors.append("ENTITY_SUMMARY requires one analyzed row per entity")
    row_ids = scope.get("fit_row_ids", [])
    if not isinstance(row_ids, list) or len(row_ids) != len(ids) or len(set(map(str, row_ids))) != len(ids):
        errors.append("ASSOCIATION_ROW_PROVENANCE_REQUIRED")
    if scope.get("claim_level") == "ADJUSTED_ASSOCIATION" and not scope.get("adjustment_variables"):
        errors.append("ADJUSTMENT_NOT_RECORDED")
    return list(dict.fromkeys(errors))


def apply_association_gate(record: Mapping, contract: Mapping, scope: Mapping) -> dict[str, Any]:
    result = copy.deepcopy(dict(record))
    result["association_contract"] = copy.deepcopy(dict(contract))
    result["association_scope"] = copy.deepcopy(dict(scope))
    errors = association_scope_errors(contract, scope)
    result["association_scope"]["gate_status"] = "FAIL" if errors else "PASS"
    if errors:
        result["status"] = "INVALIDATED"
        result["invalidation_reason"] = "; ".join(filter(None, [result.get("invalidation_reason"), *errors]))
    return result
