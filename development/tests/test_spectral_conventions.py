from __future__ import annotations

import numpy as np

from skill.scripts.spectral_conventions import (
    assess_contract,
    frequency_grid_from_fft_bins,
    reviewer_codes,
    should_activate,
)


def base_contract(**overrides: object) -> dict:
    body = {
        "active": True,
        "signal_name": "synthetic signal",
        "signal_type": "COMPLEX",
        "sample_domain": "DISCRETE",
        "sampling_rate": 8.0,
        "sampling_interval": 1.0 / 8.0,
        "sample_count": 8,
        "observation_duration": 1.0,
        "time_unit": "s",
        "frequency_unit": "Hz",
        "angular_frequency_used": False,
        "transform_type": "FFT",
        "transform_length": 8,
        "transform_axis": 0,
        "transform_normalization": {"forward": "unscaled DFT", "inverse": "1/N"},
        "frequency_grid_definition": "unshifted fftfreq grid in Hz",
        "negative_frequency_ordering": "positive bins then negative bins; fftshift when plotted",
        "one_or_two_sided": "TWO_SIDED",
        "window": "none",
        "window_normalization": "not applicable",
        "leakage_checked": True,
        "zero_padding": False,
        "amplitude_quantity": "complex spectrum amplitude",
        "absolute_spectral_claim": True,
        "power_definition": "abs(x)^2",
        "psd_used": False,
        "phase_representation": "wrapped angle in [-pi, pi)",
        "unwrap_used": False,
        "bin_spacing": 1.0,
        "claimed_resolution": "not claimed",
        "resolution_basis": "observation duration and estimator",
        "aliasing_checked": True,
        "target_frequency_max": 3.0,
        "validation_evidence": ["known tone", "fft ifft reconstruction"],
        "status": "SPECTRAL_CONVENTION_VERIFIED",
    }
    body.update(overrides)
    return {"spectral_convention": body}


def test_activation_boundary_does_not_touch_tabular_tasks() -> None:
    assert should_activate("ordinary tabular regression") is False
    assert should_activate("estimate a sampled signal with an FFT") is True


def test_a_known_positive_complex_tone_maps_to_positive_hz() -> None:
    fs = 8.0
    x = np.exp(2j * np.pi * 2 * np.arange(8) / fs)
    spectrum = np.fft.fft(x)
    grid = np.asarray(frequency_grid_from_fft_bins(fs, len(x)))
    assert grid[int(np.argmax(np.abs(spectrum)))] == 2.0
    assert reviewer_codes(base_contract()) == []


def test_b_known_negative_complex_tone_maps_to_negative_hz() -> None:
    fs = 8.0
    x = np.exp(-2j * np.pi * 2 * np.arange(8) / fs)
    spectrum = np.fft.fft(x)
    grid = np.asarray(frequency_grid_from_fft_bins(fs, len(x)))
    assert grid[int(np.argmax(np.abs(spectrum)))] == -2.0
    assert frequency_grid_from_fft_bins(8.0, 8)[4] == -4.0


def test_c_hz_and_angular_frequency_mismatch_is_guarded() -> None:
    contract = base_contract(formula_frequency_unit="rad/s")
    assert "FREQUENCY_UNIT_MISMATCH" in reviewer_codes(contract)


def test_d_fft_ifft_reconstruction_passes() -> None:
    x = np.array([1 + 1j, -2 + 0.5j, 3 - 1j, 0.25j])
    assert np.max(np.abs(np.fft.ifft(np.fft.fft(x)) - x)) < 1e-12
    assert assess_contract(base_contract(sample_count=4, transform_length=4, observation_duration=0.5, bin_spacing=2.0))["status"] == "SPECTRAL_CONVENTION_VERIFIED"


def test_e_parseval_holds_for_complex_signal() -> None:
    x = np.array([1 + 1j, -2 + 0.5j, 3 - 1j, 0.25j])
    X = np.fft.fft(x)
    assert np.isclose(np.sum(np.abs(x) ** 2), np.sum(np.abs(X) ** 2) / len(x))


def test_f_complex_power_rejects_literal_square_and_accepts_magnitude_square() -> None:
    invalid = base_contract(power_definition="x^2")
    assert "COMPLEX_POWER_DEFINITION_INVALID" in reviewer_codes(invalid)
    assert np.isclose(abs(1 + 1j) ** 2, 2.0)
    assert "COMPLEX_POWER_DEFINITION_INVALID" not in reviewer_codes(base_contract())


def test_g_one_sided_real_spectrum_declares_sidedness() -> None:
    fs = 8.0
    x = np.cos(2 * np.pi * 2 * np.arange(8) / fs)
    X = np.fft.rfft(x)
    assert np.argmax(np.abs(X)) == 2
    contract = base_contract(signal_type="REAL", one_or_two_sided="ONE_SIDED", power_definition="real one-sided power", absolute_spectral_claim=True)
    assert "SPECTRUM_SIDEDNESS_UNVERIFIED" not in reviewer_codes(contract)


def test_h_zero_padding_cannot_claim_new_physical_resolution() -> None:
    contract = base_contract(zero_padding=16, zero_padding_resolution_claim=True)
    assert "ZERO_PADDING_AS_RESOLUTION_GAIN" in reviewer_codes(contract)


def test_i_bin_spacing_is_not_effective_resolution() -> None:
    contract = base_contract(resolution_basis="BIN_SPACING")
    assert "BIN_SPACING_AS_RESOLUTION" in reviewer_codes(contract)


def test_j_aliasing_risk_is_unverified_without_band_limit() -> None:
    contract = base_contract(target_frequency_max=5.0, aliasing_checked=False)
    assert "ALIASING_UNVERIFIED" in reviewer_codes(contract)


def test_k_validated_phase_unwrap_is_accepted() -> None:
    wrapped = np.angle(np.exp(1j * np.linspace(-3 * np.pi, 3 * np.pi, 32)))
    recovered = np.unwrap(wrapped)
    assert np.max(np.abs(np.diff(recovered, 2))) < 1.0
    contract = base_contract(unwrap_used=True, phase_unwrap_validated=True, phase_representation="unwrapped phase after validated unwrap")
    assert "PHASE_UNWRAP_UNVERIFIED" not in reviewer_codes(contract)


def test_l_psd_metadata_is_conditional() -> None:
    no_psd = base_contract(psd_used=False, psd_definition="", psd_unit="", bandwidth_normalization="")
    assert "SPECTRAL_DENSITY_NORMALIZATION_INVALID" not in reviewer_codes(no_psd)
    missing = base_contract(psd_used=True)
    assert "SPECTRAL_DENSITY_NORMALIZATION_INVALID" in reviewer_codes(missing)
    valid = base_contract(
        psd_used=True,
        psd_definition="two-sided periodogram per bin bandwidth",
        psd_unit="quantity^2/Hz",
        bandwidth_normalization="divide by Fs",
    )
    assert "SPECTRAL_DENSITY_NORMALIZATION_INVALID" not in reviewer_codes(valid)


def test_m_wrong_transform_axis_is_reported() -> None:
    contract = base_contract(input_shape=[2, 8], transform_axis=1, actual_transform_axis=0)
    assert "TRANSFORM_AXIS_UNVERIFIED" in reviewer_codes(contract)


def test_n_non_rectangular_window_requires_amplitude_normalization() -> None:
    contract = base_contract(window="hann", window_normalization="")
    result = assess_contract(contract)
    assert "WINDOW_NORMALIZATION_UNVERIFIED" in result["reviewer_codes"]
    assert result["status"] != "SPECTRAL_CONVENTION_VERIFIED"
