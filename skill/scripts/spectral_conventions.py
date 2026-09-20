"""Validation helpers for a lightweight spectral convention contract.

The module validates declarations around sampled signals and frequency-domain
quantities. It deliberately does not implement FFT, PSD, filtering, or phase
estimation algorithms; callers remain responsible for using a numerical
library and recording the resulting provenance.
"""

from __future__ import annotations

import math
import re
from collections.abc import Mapping, Sequence
from typing import Any


SIGNAL_TYPES = {"REAL", "COMPLEX"}
SAMPLE_DOMAINS = {"DISCRETE", "CONTINUOUS_SAMPLED"}
SIDEDNESS = {"ONE_SIDED", "TWO_SIDED"}
FREQUENCY_UNITS = {"HZ", "RAD/S", "RAD_PER_S", "RAD\u00b7S^-1"}
TRANSFORM_TYPES = {"DFT", "FFT", "IFFT", "FREQUENCY_DOMAIN_FILTER", "OTHER"}
STATUSES = {
    "SPECTRAL_CONVENTION_VERIFIED",
    "SPECTRAL_CONVENTION_PARTIAL",
    "SPECTRAL_CONVENTION_UNVERIFIED",
}

REVIEWER_CODES = {
    "FREQUENCY_AXIS_UNVERIFIED",
    "FREQUENCY_UNIT_MISMATCH",
    "TRANSFORM_NORMALIZATION_UNVERIFIED",
    "COMPLEX_POWER_DEFINITION_INVALID",
    "SPECTRUM_SIDEDNESS_UNVERIFIED",
    "ZERO_PADDING_AS_RESOLUTION_GAIN",
    "BIN_SPACING_AS_RESOLUTION",
    "ALIASING_UNVERIFIED",
    "PHASE_UNWRAP_UNVERIFIED",
    "SPECTRAL_DENSITY_NORMALIZATION_INVALID",
    "WINDOW_NORMALIZATION_UNVERIFIED",
    "TRANSFORM_AXIS_UNVERIFIED",
}

SPECTRAL_TRIGGER_TERMS = (
    "sampled signal",
    "fft",
    "ifft",
    "dft",
    "frequency-domain",
    "frequency domain",
    "spectral",
    "transfer function",
    "convolution via frequency",
    "complex baseband",
    "instantaneous phase",
    "phase spectrum",
    "phase estimation",
    "psd",
    "asd",
    "dBc/Hz",
    "time-frequency",
)


def _body(contract: Mapping[str, Any]) -> Mapping[str, Any]:
    nested = contract.get("spectral_convention")
    return nested if isinstance(nested, Mapping) else contract


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _normalise_unit(value: Any) -> str:
    return str(value or "").strip().upper().replace(" ", "")


def _truthy(value: Any) -> bool:
    return value is True or str(value).strip().upper() in {"TRUE", "YES", "PASS", "CHECKED"}


def _has_text(value: Any) -> bool:
    return bool(str(value or "").strip())


def _contains_any(value: Any, terms: Sequence[str]) -> bool:
    text = str(value or "").lower()
    return any(term.lower() in text for term in terms)


def should_activate(task_description: str) -> bool:
    """Return whether the task description crosses the spectral activation boundary."""
    text = str(task_description or "").lower()
    return any(term.lower() in text for term in SPECTRAL_TRIGGER_TERMS)


def validate_contract(contract: Mapping[str, Any]) -> list[str]:
    """Return structural errors without inferring a status."""
    if not isinstance(contract, Mapping):
        return ["contract must be a mapping"]
    body = _body(contract)
    errors: list[str] = []
    for field in ("signal_name", "signal_type", "sample_domain", "frequency_unit"):
        if not _has_text(body.get(field)):
            errors.append(f"missing contract field: {field}")
    if body.get("signal_type") not in SIGNAL_TYPES:
        errors.append(f"invalid signal_type: {body.get('signal_type')}")
    if body.get("sample_domain") not in SAMPLE_DOMAINS:
        errors.append(f"invalid sample_domain: {body.get('sample_domain')}")
    if _normalise_unit(body.get("frequency_unit")) not in FREQUENCY_UNITS:
        errors.append(f"invalid frequency_unit: {body.get('frequency_unit')}")
    transform_type = body.get("transform_type")
    if transform_type is not None and transform_type not in TRANSFORM_TYPES:
        errors.append(f"invalid transform_type: {transform_type}")
    sidedness = body.get("one_or_two_sided")
    if sidedness is not None and sidedness not in SIDEDNESS:
        errors.append(f"invalid one_or_two_sided: {sidedness}")
    if body.get("unwrap_used") is not None and not isinstance(body.get("unwrap_used"), bool):
        errors.append("unwrap_used must be boolean")
    if body.get("psd_used") is not None and not isinstance(body.get("psd_used"), bool):
        errors.append("psd_used must be boolean")
    if body.get("zero_padding") is not None and not isinstance(body.get("zero_padding"), (bool, int)):
        errors.append("zero_padding must be boolean or integer")
    for field in ("sample_count", "transform_length"):
        value = body.get(field)
        if value is not None and (not isinstance(value, int) or isinstance(value, bool) or value <= 0):
            errors.append(f"{field} must be a positive integer")
    axis = body.get("transform_axis")
    if axis is not None and (not isinstance(axis, int) or isinstance(axis, bool)):
        errors.append("transform_axis must be an integer axis")
    if body.get("validation_evidence") is not None and not isinstance(body.get("validation_evidence"), Sequence):
        errors.append("validation_evidence must be a list")
    return errors


def sampling_identity(contract: Mapping[str, Any], *, relative_tolerance: float = 1e-9) -> dict[str, Any]:
    """Check Fs, dt, N, T and transform-bin spacing when declared."""
    body = _body(contract)
    fs = body.get("sampling_rate")
    dt = body.get("sampling_interval")
    n = body.get("sample_count")
    duration = body.get("observation_duration")
    transform_length = body.get("transform_length") or n
    checks: dict[str, bool] = {}
    errors: list[str] = []

    if _is_number(fs) and _is_number(dt):
        checks["dt_equals_inverse_sampling_rate"] = math.isclose(float(dt), 1.0 / float(fs), rel_tol=relative_tolerance, abs_tol=0.0)
        if not checks["dt_equals_inverse_sampling_rate"]:
            errors.append("sampling_interval is not 1 / sampling_rate")
    else:
        checks["dt_equals_inverse_sampling_rate"] = False
    if _is_number(fs) and _is_number(n) and _is_number(duration) and _is_number(dt):
        checks["duration_equals_n_dt"] = math.isclose(float(duration), float(n) * float(dt), rel_tol=relative_tolerance, abs_tol=0.0)
        if not checks["duration_equals_n_dt"]:
            errors.append("observation_duration is not sample_count * sampling_interval")
    else:
        checks["duration_equals_n_dt"] = False
    if _is_number(fs) and isinstance(transform_length, int) and transform_length > 0:
        expected = float(fs) / transform_length
        declared = body.get("bin_spacing")
        checks["bin_spacing_equals_fs_over_transform_length"] = _is_number(declared) and math.isclose(
            float(declared), expected, rel_tol=relative_tolerance, abs_tol=0.0
        )
        if not checks["bin_spacing_equals_fs_over_transform_length"]:
            errors.append("bin_spacing is not sampling_rate / transform_length")
    else:
        checks["bin_spacing_equals_fs_over_transform_length"] = False
    checks["complete"] = all(checks.values())
    return {
        "sampling_rate": fs,
        "sampling_interval": dt,
        "sample_count": n,
        "observation_duration": duration,
        "transform_length": transform_length,
        "checks": checks,
        "errors": errors,
    }


def _normalization_declared(body: Mapping[str, Any]) -> bool:
    value = body.get("transform_normalization")
    if isinstance(value, Mapping):
        return _has_text(value.get("forward")) and _has_text(value.get("inverse"))
    return _has_text(value)


def _absolute_quantity_claim(body: Mapping[str, Any]) -> bool:
    return bool(
        _has_text(body.get("amplitude_quantity"))
        or _has_text(body.get("power_definition"))
        or _truthy(body.get("absolute_spectral_claim"))
        or body.get("psd_used") is True
        or body.get("asd_used") is True
    )


def reviewer_codes(contract: Mapping[str, Any]) -> list[str]:
    """Return deterministic reviewer guard codes for a contract."""
    if not isinstance(contract, Mapping):
        return ["FREQUENCY_AXIS_UNVERIFIED", "TRANSFORM_NORMALIZATION_UNVERIFIED"]
    body = _body(contract)
    codes: set[str] = set()
    identity = sampling_identity(contract)
    if body.get("sample_domain") in SAMPLE_DOMAINS:
        if not _has_text(body.get("frequency_grid_definition")) or not identity["checks"].get("bin_spacing_equals_fs_over_transform_length", False):
            codes.add("FREQUENCY_AXIS_UNVERIFIED")

    frequency_unit = _normalise_unit(body.get("frequency_unit"))
    formula_unit = _normalise_unit(body.get("formula_frequency_unit"))
    conversion = body.get("frequency_conversion")
    if formula_unit and frequency_unit and formula_unit != frequency_unit and not _has_text(conversion):
        codes.add("FREQUENCY_UNIT_MISMATCH")
    if body.get("angular_frequency_used") is True and frequency_unit == "HZ" and not _has_text(conversion):
        codes.add("FREQUENCY_UNIT_MISMATCH")

    if _absolute_quantity_claim(body) and not _normalization_declared(body):
        codes.add("TRANSFORM_NORMALIZATION_UNVERIFIED")

    if body.get("signal_type") == "COMPLEX":
        power = str(body.get("power_definition") or "").replace(" ", "").lower()
        if power and ("x^2" in power or "x**2" in power or power in {"x2", "square(x)"}):
            codes.add("COMPLEX_POWER_DEFINITION_INVALID")
        if not power or not any(token in power for token in ("abs", "conj", "|x|", "magnitude")):
            codes.add("COMPLEX_POWER_DEFINITION_INVALID")

    if _absolute_quantity_claim(body) and body.get("one_or_two_sided") not in SIDEDNESS:
        codes.add("SPECTRUM_SIDEDNESS_UNVERIFIED")

    if body.get("zero_padding") not in (None, False, 0) and (
        _truthy(body.get("zero_padding_resolution_claim"))
        or _contains_any(body.get("claimed_resolution_basis"), ("zero", "padding", "grid"))
    ):
        codes.add("ZERO_PADDING_AS_RESOLUTION_GAIN")

    resolution_basis = str(body.get("resolution_basis") or body.get("claimed_resolution_basis") or "").upper()
    if resolution_basis in {"BIN_SPACING", "FS/N", "FFT_BIN", "BIN"} or _truthy(body.get("resolution_equals_bin_spacing")):
        codes.add("BIN_SPACING_AS_RESOLUTION")

    target_max = body.get("target_frequency_max")
    if _is_number(target_max) and _is_number(body.get("sampling_rate")):
        nyquist = float(body["sampling_rate"]) / 2.0
        if abs(float(target_max)) > nyquist and not _has_text(body.get("anti_aliasing_mechanism")) and not _has_text(body.get("source_band_constraint")):
            codes.add("ALIASING_UNVERIFIED")
    elif body.get("aliasing_checked") not in (True, "NOT_APPLICABLE", "NOT_CLAIMED") and body.get("sample_domain") in SAMPLE_DOMAINS:
        codes.add("ALIASING_UNVERIFIED")

    if body.get("unwrap_used") is True and not (
        _truthy(body.get("phase_unwrap_validated"))
        or _has_text(body.get("phase_unwrap_condition"))
        or _has_text(body.get("phase_unwrap_validation"))
    ):
        codes.add("PHASE_UNWRAP_UNVERIFIED")

    psd_claim = body.get("psd_used") is True or body.get("asd_used") is True or _contains_any(body.get("spectral_quantity"), ("psd", "asd", "density", "dBc/Hz"))
    if psd_claim:
        unit = str(body.get("psd_unit") or body.get("density_unit") or "").lower()
        definition = body.get("psd_definition") or body.get("density_definition")
        bandwidth = body.get("bandwidth_normalization") or body.get("bin_width_normalization")
        expected = "sqrt(hz)" if body.get("asd_used") is True else "/hz"
        if not _has_text(definition) or not _has_text(bandwidth) or expected not in unit:
            codes.add("SPECTRAL_DENSITY_NORMALIZATION_INVALID")

    window = str(body.get("window") or "").strip().lower()
    non_rectangular = window not in {"", "none", "rectangular", "boxcar"}
    if non_rectangular and _absolute_quantity_claim(body) and not _has_text(body.get("window_normalization")):
        codes.add("WINDOW_NORMALIZATION_UNVERIFIED")

    shape = body.get("input_shape")
    if isinstance(shape, Sequence) and not isinstance(shape, (str, bytes, bytearray)) and len(shape) > 1 and body.get("transform_axis") is None:
        codes.add("TRANSFORM_AXIS_UNVERIFIED")
    if shape is not None and body.get("transform_axis") is not None and body.get("actual_transform_axis") is not None:
        if body.get("transform_axis") != body.get("actual_transform_axis"):
            codes.add("TRANSFORM_AXIS_UNVERIFIED")
    return sorted(codes)


def derive_status(contract: Mapping[str, Any]) -> str:
    """Derive a conservative status from schema, identities, guards, and evidence."""
    errors = validate_contract(contract)
    if errors:
        return "SPECTRAL_CONVENTION_UNVERIFIED"
    body = _body(contract)
    codes = reviewer_codes(contract)
    identity = sampling_identity(contract)
    evidence = body.get("validation_evidence")
    has_evidence = isinstance(evidence, Sequence) and len(evidence) > 0
    if codes or not identity["checks"].get("complete", False):
        return "SPECTRAL_CONVENTION_PARTIAL" if body.get("status") == "SPECTRAL_CONVENTION_PARTIAL" or has_evidence else "SPECTRAL_CONVENTION_UNVERIFIED"
    if not has_evidence:
        return "SPECTRAL_CONVENTION_PARTIAL"
    return "SPECTRAL_CONVENTION_VERIFIED"


def assess_contract(contract: Mapping[str, Any]) -> dict[str, Any]:
    """Return the complete deterministic audit result."""
    errors = validate_contract(contract)
    identity = sampling_identity(contract)
    codes = reviewer_codes(contract)
    status = derive_status(contract)
    return {
        "status": status,
        "schema_errors": errors,
        "reviewer_codes": codes,
        "sampling_identity": identity,
        "claim_allowed": status == "SPECTRAL_CONVENTION_VERIFIED",
    }


def frequency_grid_from_fft_bins(sampling_rate: float, transform_length: int) -> list[float]:
    """Return the mathematical two-sided FFT bin grid without performing a transform."""
    if not _is_number(sampling_rate) or not isinstance(transform_length, int) or transform_length <= 0:
        raise ValueError("sampling_rate and transform_length must be valid")
    step = float(sampling_rate) / transform_length
    positive_limit = (transform_length - 1) // 2
    return [index * step if index <= positive_limit else (index - transform_length) * step for index in range(transform_length)]


__all__ = [
    "REVIEWER_CODES",
    "assess_contract",
    "derive_status",
    "frequency_grid_from_fft_bins",
    "reviewer_codes",
    "sampling_identity",
    "should_activate",
    "validate_contract",
]
