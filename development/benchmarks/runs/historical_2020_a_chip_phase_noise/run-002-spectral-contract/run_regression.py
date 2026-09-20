from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[5]
RUN1 = ROOT / "development/benchmarks/runs/historical_2020_a_chip_phase_noise/run-001"
REFERENCE = ROOT / "development/benchmarks/runs/historical_2020_a_chip_phase_noise/reference-benchmark"
sys.path.insert(0, str(ROOT))

from skill.scripts.spectral_conventions import assess_contract, frequency_grid_from_fft_bins


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    fs = 150e9
    n = 32768
    dt = 1.0 / fs
    contract = {
        "spectral_convention": {
            "active": True,
            "signal_name": "2020A run-001 complex symbol / dispersion block",
            "signal_type": "COMPLEX",
            "sample_domain": "DISCRETE",
            "sampling_rate": fs,
            "sampling_interval": dt,
            "sample_count": n,
            "observation_duration": n * dt,
            "time_unit": "s",
            "frequency_unit": "Hz",
            "formula_frequency_unit": "Hz",
            "angular_frequency_used": False,
            "transform_type": "FFT",
            "transform_length": n,
            "transform_axis": 0,
            "actual_transform_axis": 0,
            "transform_normalization": {"forward": "NumPy default unscaled DFT", "inverse": "NumPy default inverse divided by N"},
            "frequency_grid_definition": "numpy.fft.fftfreq(N, d=1/Fs), two-sided Hz grid",
            "negative_frequency_ordering": "unshifted bins; negative bins after the positive half",
            "one_or_two_sided": "TWO_SIDED",
            "window": "none",
            "window_normalization": "not_applicable",
            "leakage_checked": True,
            "zero_padding": False,
            "zero_padding_resolution_claim": False,
            "amplitude_quantity": "complex time-domain symbol amplitude",
            "absolute_spectral_claim": False,
            "power_definition": "|x|^2 for complex signal power",
            "psd_used": False,
            "asd_used": False,
            "phase_representation": "wrapped angle; explicit unwrap for pilot interpolation",
            "unwrap_used": True,
            "phase_unwrap_validated": True,
            "phase_unwrap_condition": "run-001 known phase sequence synthetic check",
            "bin_spacing": fs / n,
            "claimed_resolution": "not claimed",
            "resolution_basis": "observation duration and dispersion model/block assumptions",
            "resolution_equals_bin_spacing": False,
            "aliasing_checked": "NOT_CLAIMED",
            "validation_evidence": ["Parseval", "dispersion reconstruction", "phase unwrap"],
        }
    }

    audit = assess_contract(contract)
    grid = np.asarray(frequency_grid_from_fft_bins(fs, n))
    numpy_grid = np.fft.fftfreq(n, d=dt)

    rng = np.random.default_rng(202009)
    x = rng.normal(size=256) + 1j * rng.normal(size=256)
    transfer = np.exp(1j * 0.0007 * np.arange(256))
    dispersed = np.fft.ifft(np.fft.fft(x) * transfer)
    reconstructed = np.fft.ifft(np.fft.fft(dispersed) * np.conj(transfer))
    wrapped = np.angle(np.exp(1j * np.linspace(-3 * np.pi, 3 * np.pi, 64)))
    unwrapped = np.unwrap(wrapped)

    runtime = json.loads((RUN1 / "work/runtime-provenance.json").read_text(encoding="utf-8"))
    reference_completion = json.loads((REFERENCE / "completion.json").read_text(encoding="utf-8"))
    frozen_status = "BLIND_RUN_PARTIAL" if "BLIND_RUN_PARTIAL" in (RUN1 / "REPORT.md").read_text(encoding="utf-8") else "CHANGED"
    results = {
        "status": "2020A_SPECTRAL_CONTRACT_TARGETED_REGRESSION_COMPLETE",
        "contract_status": audit["status"],
        "reviewer_codes": audit["reviewer_codes"],
        "sampling_identity": audit["sampling_identity"],
        "frequency_grid_matches_numpy_fftfreq": bool(np.array_equal(grid, numpy_grid)),
        "negative_frequency_examples_hz": [float(grid[1]), float(grid[n // 2]), float(grid[n // 2 + 1]), float(grid[-1])],
        "fft_ifft_reconstruction_max_abs": float(np.max(np.abs(np.fft.ifft(np.fft.fft(x)) - x))),
        "dispersion_reconstruction_max_abs": float(np.max(np.abs(reconstructed - x))),
        "parseval_relative_error": float(abs(np.sum(abs(x) ** 2) - np.sum(abs(np.fft.fft(x)) ** 2) / len(x)) / np.sum(abs(x) ** 2)),
        "complex_power_1_plus_1j": float(abs(1 + 1j) ** 2),
        "phase_unwrap_max_second_difference": float(np.max(np.abs(np.diff(unwrapped, 2)))),
        "psd_used": contract["spectral_convention"]["psd_used"],
        "bin_spacing_hz": fs / n,
        "resolution_claim": "not claimed",
        "runtime_evidence": {
            "frame_n": runtime.get("frame_n"),
            "fft_length": runtime.get("fft_length"),
            "normalization": runtime.get("normalization"),
            "window": runtime.get("window"),
            "zero_padding": runtime.get("zero_padding"),
        },
        "frozen_2020a_status": frozen_status,
        "ber_threshold_provenance": reference_completion.get("ber_threshold_status"),
        "channel_order_provenance": reference_completion.get("channel_order_status"),
        "dispersion_convention": reference_completion.get("dispersion_convention_status"),
        "frozen_input_sha256": {
            "run-001/REPORT.md": sha256(RUN1 / "REPORT.md"),
            "run-001/signal-ledger.md": sha256(RUN1 / "signal-ledger.md"),
            "run-001/work/runtime-provenance.json": sha256(RUN1 / "work/runtime-provenance.json"),
            "reference-benchmark/completion.json": sha256(REFERENCE / "completion.json"),
        },
    }
    output = Path(__file__).with_name("results.json")
    with output.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))
    required = [
        audit["status"] == "SPECTRAL_CONVENTION_VERIFIED",
        not audit["reviewer_codes"],
        audit["sampling_identity"]["checks"]["complete"],
        results["frequency_grid_matches_numpy_fftfreq"],
        results["dispersion_reconstruction_max_abs"] < 1e-12,
        results["parseval_relative_error"] < 1e-12,
        abs(results["complex_power_1_plus_1j"] - 2.0) < 1e-12,
        results["frozen_2020a_status"] == "BLIND_RUN_PARTIAL",
        results["ber_threshold_provenance"] == "REFERENCE_CONSENSUS_ONLY",
        results["channel_order_provenance"] == "REFERENCE_CONSENSUS_ONLY",
        results["dispersion_convention"] == "MIXED_REFERENCES",
    ]
    return 0 if all(required) else 1


if __name__ == "__main__":
    raise SystemExit(main())
