from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


FS = 150e9
LAMBDA = 1550e-9
C_LIGHT = 299792458.0
PARALLELISM = 128
BER_MAIN = 1e-2
BER_SENSITIVITY = 1e-3
FRAME_N = 65536
PILOT_SYMBOL = (3.0 + 3.0j) / math.sqrt(10.0)
GRAY_BITS = np.array([[0, 0], [0, 1], [1, 1], [1, 0]], dtype=np.uint8)
QAM_LEVELS = np.array([-3.0, -1.0, 1.0, 3.0]) / math.sqrt(10.0)


def stable_seed(*parts: object) -> int:
    raw = "|".join(map(str, parts)).encode("utf-8")
    return int.from_bytes(hashlib.sha256(raw).digest()[:8], "big") % (2**32 - 1)


def bits_to_symbols(bits: np.ndarray) -> np.ndarray:
    idx_i = bits[:, 0] * 2 + bits[:, 1]
    idx_q = bits[:, 2] * 2 + bits[:, 3]
    # Gray code index order 00, 01, 11, 10.
    gray_to_level = np.array([0, 1, 3, 2], dtype=np.int64)
    return QAM_LEVELS[gray_to_level[idx_i]] + 1j * QAM_LEVELS[gray_to_level[idx_q]]


def symbols_to_bits(symbols: np.ndarray) -> np.ndarray:
    i_idx = np.argmin(np.abs(symbols.real[:, None] - QAM_LEVELS[None, :]), axis=1)
    q_idx = np.argmin(np.abs(symbols.imag[:, None] - QAM_LEVELS[None, :]), axis=1)
    return np.concatenate([GRAY_BITS[i_idx], GRAY_BITS[q_idx]], axis=1)


def dispersion_transfer(n: int, dz_ps_nm: float) -> np.ndarray:
    # Cumulative ps/nm converts to seconds/metre: 1 ps/nm = 1e-3 s/m.
    d_si = float(dz_ps_nm) * 1e-3
    f_hz = np.fft.fftfreq(n, d=1.0 / FS)
    return np.exp(1j * np.pi * LAMBDA**2 * d_si / C_LIGHT * f_hz**2)


def quantize_real(x: np.ndarray, bits: int, frac_bits: int) -> np.ndarray:
    scale = 2.0**frac_bits
    lo = -(2 ** (bits - 1))
    hi = 2 ** (bits - 1) - 1
    return np.clip(np.rint(x * scale), lo, hi) / scale


def quantize_complex(x: np.ndarray, bits: int) -> np.ndarray:
    frac_bits = max(bits - 2, 0)
    return quantize_real(x.real, bits, frac_bits) + 1j * quantize_real(x.imag, bits, frac_bits)


def quantize_phase(phi: np.ndarray, bits: int) -> np.ndarray:
    step = 2.0 * np.pi / (2**bits)
    wrapped = (phi + np.pi) % (2.0 * np.pi) - np.pi
    return np.rint(wrapped / step) * step


def make_frame(n: int, seed: int, period: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    raw_bits = rng.integers(0, 2, size=(n, 4), dtype=np.uint8)
    raw_symbols = bits_to_symbols(raw_bits)
    pilot_mask = np.zeros(n, dtype=bool)
    pilot_mask[::period] = True
    tx = raw_symbols.copy()
    tx[pilot_mask] = PILOT_SYMBOL
    return raw_bits, raw_symbols, tx, pilot_mask


def moving_average(values: np.ndarray, width: int) -> np.ndarray:
    if width <= 1:
        return values.copy()
    left = width // 2
    right = width - 1 - left
    padded = np.pad(values, (left, right), mode="edge")
    return np.convolve(padded, np.ones(width) / width, mode="valid")


def simulate(
    *,
    snr_db: float,
    lw_khz: float,
    dz_ps_nm: float,
    period: int,
    method: str,
    n: int = FRAME_N,
    seed: int = 202009,
    rx_bits: int | None = None,
    phase_bits: int | None = None,
    phase_noise_enabled: bool = True,
    channel_order: str = "dispersion_then_phase",
) -> dict:
    raw_bits, raw_symbols, tx, pilot_mask = make_frame(n, stable_seed(seed, "frame", n), period)
    h = dispersion_transfer(n, dz_ps_nm)
    rng = np.random.default_rng(stable_seed(seed, "channel", snr_db, lw_khz, dz_ps_nm, n))
    if phase_noise_enabled:
        linewidth_hz = lw_khz * 1e3
        increments = rng.normal(0.0, math.sqrt(2.0 * np.pi * linewidth_hz / FS), size=n)
        theta = np.cumsum(increments)
    else:
        theta = np.zeros(n)
    noise_power = 10.0 ** (-snr_db / 10.0)
    awgn = math.sqrt(noise_power / 2.0) * (rng.normal(size=n) + 1j * rng.normal(size=n))
    if channel_order == "dispersion_then_phase":
        dispersed = np.fft.ifft(np.fft.fft(tx) * h)
        received = dispersed * np.exp(1j * theta) + awgn
    elif channel_order == "phase_then_dispersion":
        phase_first = tx * np.exp(1j * theta)
        received = np.fft.ifft(np.fft.fft(phase_first) * h) + awgn
    else:
        raise ValueError(f"unknown channel_order: {channel_order}")
    if rx_bits is not None:
        received = quantize_complex(received, rx_bits)

    # Exact known dispersion compensation is excluded from the resource score by the problem.
    compensated_dispersion = np.fft.ifft(np.fft.fft(received) * np.conj(h))
    if not phase_noise_enabled:
        phase_hat = np.zeros(n)
    else:
        pilot_idx = np.flatnonzero(pilot_mask)
        pilot_phase_wrapped = np.angle(compensated_dispersion[pilot_idx] * np.conj(PILOT_SYMBOL))
        pilot_phase = np.unwrap(pilot_phase_wrapped)
        if method == "linear_smooth3":
            pilot_phase = moving_average(pilot_phase, 3)
        elif method not in {"linear", "nearest", "linear_dd"}:
            raise ValueError(f"unknown method: {method}")
        if method == "nearest":
            positions = np.searchsorted(pilot_idx, np.arange(n), side="right") - 1
            positions = np.clip(positions, 0, len(pilot_idx) - 1)
            phase_hat = pilot_phase[positions]
        else:
            phase_hat = np.interp(np.arange(n), pilot_idx, pilot_phase)
        if phase_bits is not None:
            phase_hat = quantize_phase(phase_hat, phase_bits)

    corrected = compensated_dispersion * np.exp(-1j * phase_hat)
    if phase_noise_enabled and method == "linear_dd":
        # Low-capacity decision-directed residual tracker: one LUT phase error and
        # one first-order accumulator per symbol. Alpha is fixed before evaluation.
        provisional = symbols_to_bits(corrected)
        provisional_symbols = bits_to_symbols(provisional)
        residual_error = np.angle(corrected * np.conj(provisional_symbols))
        residual = np.zeros(n)
        alpha = 0.90
        for k in range(1, n):
            residual[k] = alpha * residual[k - 1] + (1.0 - alpha) * residual_error[k]
        if phase_bits is not None:
            residual = quantize_phase(residual, phase_bits)
        phase_hat = phase_hat + residual
        corrected = compensated_dispersion * np.exp(-1j * phase_hat)
    decisions = symbols_to_bits(corrected)
    payload = ~pilot_mask
    bit_errors = int(np.count_nonzero(decisions[payload] != raw_bits[payload]))
    bit_count = int(np.count_nonzero(payload) * 4)
    return {
        "ber": bit_errors / bit_count,
        "bit_errors": bit_errors,
        "bit_count": bit_count,
        "snr_db": snr_db,
        "lw_khz": lw_khz,
        "dz_ps_nm": dz_ps_nm,
        "period": period,
        "pilot_overhead": 1.0 / period,
        "method": method,
        "rx_bits": rx_bits,
        "phase_bits": phase_bits,
        "n": n,
        "seed": seed,
    }


def threshold_search(
    *,
    lw_khz: float,
    dz_ps_nm: float,
    period: int,
    method: str,
    target_ber: float,
    n: int,
    seed: int,
    rx_bits: int | None = None,
    phase_bits: int | None = None,
    snr_grid: np.ndarray | None = None,
    phase_noise_enabled: bool = True,
) -> tuple[float, list[dict]]:
    grid = np.arange(8.0, 20.01, 0.5) if snr_grid is None else snr_grid
    records = [simulate(snr_db=float(s), lw_khz=lw_khz, dz_ps_nm=dz_ps_nm, period=period, method=method, n=n, seed=seed, rx_bits=rx_bits, phase_bits=phase_bits, phase_noise_enabled=phase_noise_enabled) for s in grid]
    feasible = [r for r in records if r["ber"] <= target_ber]
    if not feasible:
        return float("nan"), records
    first = feasible[0]
    idx = records.index(first)
    if idx == 0:
        return float(first["snr_db"]), records
    prev = records[idx - 1]
    # Interpolate in log-BER to reduce grid quantization without inventing a new metric.
    y0 = math.log10(max(prev["ber"], 1.0 / prev["bit_count"]))
    y1 = math.log10(max(first["ber"], 1.0 / first["bit_count"]))
    yt = math.log10(target_ber)
    if y1 == y0:
        return float(first["snr_db"]), records
    frac = np.clip((yt - y0) / (y1 - y0), 0.0, 1.0)
    return float(prev["snr_db"] + frac * (first["snr_db"] - prev["snr_db"])), records


def feasible_at_gate(**kwargs) -> dict:
    return simulate(**kwargs)


def find_largest_feasible_period(
    *,
    lw_khz: float,
    dz_ps_nm: float,
    method: str,
    gate_snr: float,
    target_ber: float,
    periods: list[int],
    n: int,
    seed: int,
    rx_bits: int | None = None,
    phase_bits: int | None = None,
) -> tuple[int | None, list[dict]]:
    rows = []
    for period in sorted(periods, reverse=True):
        row = feasible_at_gate(snr_db=gate_snr, lw_khz=lw_khz, dz_ps_nm=dz_ps_nm, period=period, method=method, n=n, seed=seed, rx_bits=rx_bits, phase_bits=phase_bits)
        row["gate_pass"] = bool(row["ber"] <= target_ber)
        rows.append(row)
    passed = [r for r in rows if r["gate_pass"]]
    return (max(r["period"] for r in passed) if passed else None), rows


def resource_score(period: int, rx_bits: int, phase_bits: int, method: str, parallelism: int = PARALLELISM) -> dict:
    # Table-1 scaling: add(8+8)=1 U, multiply(8x8)=8 U, 8-8 LUT=128 U, 8-bit x 2048 delay=1 U.
    lut = (2 ** (2 * rx_bits) * phase_bits / 2048.0 * 128.0) * parallelism
    complex_mult = (4.0 * rx_bits * max(rx_bits, phase_bits) / 8.0) * parallelism
    complex_add = (4.0 * max(rx_bits, phase_bits) / 16.0) * parallelism
    interpolation_mult = (rx_bits * phase_bits / 8.0) * parallelism
    interpolation_add = (2.0 * max(rx_bits, phase_bits) / 16.0) * parallelism
    latency = 1 + (1 if method != "nearest" else 0) + (1 if method == "linear_smooth3" else 0)
    buffer = (2.0 * rx_bits * max(period, 1) / (8.0 * 2048.0)) * parallelism * latency
    total = lut + complex_mult + complex_add + interpolation_mult + interpolation_add + buffer
    return {"lut_u": lut, "mult_u": complex_mult + interpolation_mult, "add_u": complex_add + interpolation_add, "buffer_u": buffer, "latency_cycles": latency, "total_u": total}


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    keys = sorted({k for row in rows for k in row})
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def json_safe(value):
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {k: json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_safe(v) for v in value]
    return value


def synthetic_checks(out: Path) -> dict:
    rng = np.random.default_rng(12345)
    n = 4096
    f = np.fft.fftfreq(n, 1.0 / FS)
    tone_hz = 12.0e9
    tone = np.exp(1j * 2.0 * np.pi * tone_hz * np.arange(n) / FS)
    peak = float(f[int(np.argmax(np.abs(np.fft.fft(tone))))])
    two = np.exp(1j * 2.0 * np.pi * 7e9 * np.arange(n) / FS) + 0.6 * np.exp(1j * 2.0 * np.pi * 29e9 * np.arange(n) / FS)
    two_fft = np.abs(np.fft.fft(two))
    peak_freqs = sorted([float(f[i]) for i in np.argsort(two_fft)[-4:]])
    noise = rng.normal(size=n) + 1j * rng.normal(size=n)
    parseval = abs(np.sum(abs(noise) ** 2) - np.sum(abs(np.fft.fft(noise)) ** 2) / n) / np.sum(abs(noise) ** 2)
    phase_true = np.linspace(0.0, 5.0 * np.pi, n // 8) + 0.01 * rng.normal(size=n // 8)
    phase_unwrapped = np.unwrap(np.angle(np.exp(1j * phase_true)))
    unwrap_rmse = float(np.sqrt(np.mean((phase_unwrapped - phase_true) ** 2)))
    h = dispersion_transfer(n, 10000.0)
    x = rng.normal(size=n) + 1j * rng.normal(size=n)
    y = np.fft.ifft(np.fft.fft(x) * h)
    x_hat = np.fft.ifft(np.fft.fft(y) * np.conj(h))
    reconstruction = float(np.max(np.abs(x_hat - x)))
    result = {
        "single_tone_peak_hz": peak,
        "single_tone_error_hz": abs(peak - tone_hz),
        "two_tone_peak_candidates_hz": peak_freqs,
        "parseval_relative_error": float(parseval),
        "phase_unwrap_rmse_rad": unwrap_rmse,
        "dispersion_reconstruction_max_abs": reconstruction,
        "frequency_bin_spacing_hz": FS / n,
        "status": "PASS" if abs(peak - tone_hz) <= FS / n and parseval < 1e-12 and unwrap_rmse < 0.05 and reconstruction < 1e-12 else "FAIL",
    }
    (out / "synthetic_checks.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def make_figures(out: Path, ber_rows: list[dict], q2_rows: list[dict], q3_rows: list[dict]) -> list[str]:
    figures = []
    if ber_rows:
        plt.figure(figsize=(7, 4.5))
        labels = sorted({r["label"] for r in ber_rows})
        for label in labels:
            group = [r for r in ber_rows if r["label"] == label]
            group.sort(key=lambda r: r["snr_db"])
            plt.semilogy([r["snr_db"] for r in group], [max(r["ber"], 1e-6) for r in group], marker="o", label=label)
        plt.xlabel("SNR (dB)")
        plt.ylabel("Payload BER (dimensionless)")
        plt.title("2020A CR BER curve")
        plt.grid(True, which="both", alpha=0.3)
        plt.legend()
        p = out / "ber_vs_snr.png"
        plt.tight_layout(); plt.savefig(p, dpi=160); plt.close(); figures.append(str(p))
    if q2_rows:
        lws = sorted({float(r["lw_khz"]) for r in q2_rows})
        dzs = sorted({float(r["dz_ps_nm"]) for r in q2_rows})
        matrix = np.full((len(lws), len(dzs)), np.nan)
        for i, lw in enumerate(lws):
            for j, dz in enumerate(dzs):
                vals = [r["period"] for r in q2_rows if float(r["lw_khz"]) == lw and float(r["dz_ps_nm"]) == dz and r["period"] is not None]
                if vals: matrix[i, j] = 1.0 / max(vals)
        plt.figure(figsize=(7, 4.5)); im = plt.imshow(matrix, aspect="auto", origin="lower")
        plt.xticks(range(len(dzs)), [f"{d:g}" for d in dzs]); plt.yticks(range(len(lws)), [f"{x:g}" for x in lws])
        plt.xlabel("Cumulative dispersion D_z (ps/nm)"); plt.ylabel("Linewidth (kHz)"); plt.title("Minimum pilot overhead passing 0.3 dB gate")
        plt.colorbar(im, label="Pilot overhead (1/L)"); plt.tight_layout()
        p = out / "q2_overhead_heatmap.png"; plt.savefig(p, dpi=160); plt.close(); figures.append(str(p))
    if q3_rows:
        plt.figure(figsize=(7, 4.5)); rows = [r for r in q3_rows if r.get("robust_pass")]
        if rows:
            plt.scatter([r["resource_total_u"] for r in rows], [r["pilot_overhead"] for r in rows], c=[r["rx_bits"] for r in rows], s=60)
            plt.xlabel("Resource proxy (U)"); plt.ylabel("Pilot overhead (1/L)"); plt.title("Q3 robust feasible resource frontier"); plt.colorbar(label="Received-sample bits")
        else:
            plt.text(0.1, 0.5, "No robust candidate passed", transform=plt.gca().transAxes)
        plt.tight_layout(); p = out / "q3_resource_frontier.png"; plt.savefig(p, dpi=160); plt.close(); figures.append(str(p))
    return figures


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", type=Path, required=True)
    ap.add_argument("--n", type=int, default=FRAME_N)
    args = ap.parse_args()
    run = args.run_dir
    outputs = run / "outputs"; work = run / "work"; figures_dir = run / "figures"
    outputs.mkdir(parents=True, exist_ok=True); work.mkdir(exist_ok=True); figures_dir.mkdir(exist_ok=True)
    started = time.time()

    synth = synthetic_checks(work)
    target = BER_MAIN
    seed = 202009
    baseline_snr, baseline_rows = threshold_search(lw_khz=0.0, dz_ps_nm=0.0, period=32, method="linear", target_ber=target, n=args.n, seed=seed, phase_noise_enabled=False)

    methods = ["linear", "linear_smooth3", "linear_dd"]
    q1_rows = []
    gate_snr = baseline_snr + 0.3
    q1_periods = list(range(2, 129))
    for method in methods:
        period, rows = find_largest_feasible_period(lw_khz=100.0, dz_ps_nm=20000.0, method=method, gate_snr=gate_snr, target_ber=target, periods=q1_periods, n=args.n, seed=seed)
        q1_rows.extend([{**r, "method": method} for r in rows])
    q1_summary = []
    for method in methods:
        passed = [r for r in q1_rows if r["method"] == method and r["gate_pass"]]
        max_period = max((r["period"] for r in passed), default=None)
        best_effort = min((r for r in q1_rows if r["method"] == method), key=lambda r: r["ber"])
        q1_summary.append({"method": method, "period": max_period, "pilot_overhead": (1.0 / max_period if max_period else None), "gate_snr_db": gate_snr, "gate_ber": (next((r["ber"] for r in passed if r["period"] == max_period), None) if max_period else None), "best_effort_period": best_effort["period"], "best_effort_ber": best_effort["ber"], "gate_pass": bool(max_period is not None)})
    feasible_q1 = [r for r in q1_summary if r["period"] is not None]
    if feasible_q1:
        q1_primary = min(feasible_q1, key=lambda r: (r["pilot_overhead"], methods.index(r["method"]))); q1_status = "PASS"
    else:
        q1_primary = min(q1_summary, key=lambda r: (r["best_effort_ber"], methods.index(r["method"]))); q1_primary = {**q1_primary, "period": q1_primary["best_effort_period"], "pilot_overhead": 1.0 / q1_primary["best_effort_period"]}; q1_status = "NO_CANDIDATE_PASSES_GATE"
    q1_threshold, q1_curve = threshold_search(lw_khz=100.0, dz_ps_nm=20000.0, period=int(q1_primary["period"]), method=q1_primary["method"], target_ber=target, n=args.n, seed=seed)

    lws = [10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0, 10000.0]
    dzs = [0.0, 1000.0, 3000.0, 10000.0]
    q2_rows = []
    q2_periods = [2, 4, 8, 12, 16, 20, 24, 31, 40, 48, 64, 80, 96, 112, 128]
    for lw in lws:
        for dz in dzs:
            period, tested = find_largest_feasible_period(lw_khz=lw, dz_ps_nm=dz, method=q1_primary["method"], gate_snr=gate_snr, target_ber=target, periods=q2_periods, n=args.n, seed=seed)
            chosen = next((r for r in tested if r["period"] == period), None)
            q2_rows.append({"lw_khz": lw, "dz_ps_nm": dz, "period": period, "pilot_overhead": (1.0 / period if period else None), "gate_ber": (chosen["ber"] if chosen else None), "gate_snr_db": gate_snr, "method": q1_primary["method"]})

    q3_periods = [31, 32, 40, 48, 64, 80, 96, 128]
    q3_candidates = []
    for rx_bits in [6, 7, 8, 9]:
        for phase_bits in [6, 8, 10]:
            for period in q3_periods:
                resource = resource_score(period, rx_bits, phase_bits, q1_primary["method"])
                scenario_rows = []
                robust = True
                for lw in [10.0, 100.0, 1000.0, 10000.0]:
                    for dz in [0.0, 1000.0, 10000.0]:
                        row = simulate(snr_db=gate_snr, lw_khz=lw, dz_ps_nm=dz, period=period, method=q1_primary["method"], n=args.n, seed=seed, rx_bits=rx_bits, phase_bits=phase_bits)
                        scenario_rows.append(row)
                        robust = robust and row["ber"] <= target
                q3_candidates.append({"rx_bits": rx_bits, "phase_bits": phase_bits, "period": period, "pilot_overhead": 1.0 / period, "payload_gbaud": 150.0 * (1.0 - 1.0 / period), "robust_pass": robust, "resource_total_u": resource["total_u"], "resource": resource, "worst_case_ber": max(r["ber"] for r in scenario_rows), "method": q1_primary["method"]})
    robust_candidates = [r for r in q3_candidates if r["robust_pass"]]
    q3_best = min(robust_candidates, key=lambda r: r["resource_total_u"], default=None)

    # Q4 evaluates performance-resource tradeoff in a representative high-difficulty scenario.
    rep_lw, rep_dz = 1000.0, 10000.0
    q4_rows = []
    for cand in q3_candidates:
        if cand["period"] < 31:
            continue
        threshold, _ = threshold_search(lw_khz=rep_lw, dz_ps_nm=rep_dz, period=cand["period"], method=q1_primary["method"], target_ber=target, n=max(args.n // 2, 32768), seed=seed, rx_bits=cand["rx_bits"], phase_bits=cand["phase_bits"], snr_grid=np.arange(8.0, 20.01, 1.0))
        rsnr_cost = threshold - baseline_snr if math.isfinite(threshold) else float("inf")
        q4_rows.append({**cand, "representative_lw_khz": rep_lw, "representative_dz_ps_nm": rep_dz, "rsnr_db": threshold, "rsnr_cost_db": rsnr_cost})
    finite_q4 = [r for r in q4_rows if math.isfinite(r["rsnr_cost_db"])]
    rref = min((r["resource_total_u"] for r in finite_q4), default=1.0)
    for r in q4_rows:
        r["composite_cost"] = (r["rsnr_cost_db"] / 0.3 if math.isfinite(r["rsnr_cost_db"]) else 1e6) + 0.25 * (r["resource_total_u"] / rref)
    q4_best = min(q4_rows, key=lambda r: r["composite_cost"], default=None)

    ber_rows = [{"label": "AWGN reference", **r} for r in baseline_rows]
    ber_rows += [{"label": f"CR {q1_primary['method']} L={q1_primary['period']}", **r} for r in q1_curve]
    sensitivity = []
    for target_sens in [BER_SENSITIVITY]:
        b, _ = threshold_search(lw_khz=0.0, dz_ps_nm=0.0, period=32, method="linear", target_ber=target_sens, n=args.n, seed=seed, phase_noise_enabled=False)
        p, _ = threshold_search(lw_khz=100.0, dz_ps_nm=20000.0, period=int(q1_primary["period"]), method=q1_primary["method"], target_ber=target_sens, n=args.n, seed=seed)
        sensitivity.append({"target_ber": target_sens, "baseline_rsnr_db": b, "cr_rsnr_db": p, "rsnr_cost_db": p - b})

    write_csv(outputs / "q1_period_search.csv", q1_rows)
    write_csv(outputs / "q1_summary.csv", q1_summary)
    write_csv(outputs / "q1_ber_curve.csv", ber_rows)
    write_csv(outputs / "q2_overhead_grid.csv", q2_rows)
    write_csv(outputs / "q3_candidates.csv", q3_candidates)
    write_csv(outputs / "q4_tradeoff.csv", q4_rows)
    write_csv(outputs / "sensitivity.csv", sensitivity)
    figures = make_figures(figures_dir, ber_rows, q2_rows, q3_candidates)

    summary = {
        "run_id": "historical_2020_a_chip_phase_noise/run-001",
        "problem": "2020A Huawei chip phase-noise algorithm design",
        "python": "system Python with numpy/scipy/matplotlib",
        "numpy_version": np.__version__,
        "frame_n": args.n,
        "sampling_rate_hz": FS,
        "parallelism": PARALLELISM,
        "main_ber_threshold": target,
        "sensitivity": sensitivity,
        "baseline_rsnr_db": baseline_snr,
        "q1": {"status": q1_status, "summary": q1_summary, "primary": q1_primary, "rsnr_db": q1_threshold, "rsnr_cost_db": q1_threshold - baseline_snr},
        "q2": {"rows": q2_rows, "method": q1_primary["method"]},
        "q3": {"best_robust": q3_best, "robust_candidate_count": len(robust_candidates)},
        "q4": {"representative": {"lw_khz": rep_lw, "dz_ps_nm": rep_dz}, "best": q4_best},
        "synthetic_checks": synth,
        "figures": figures,
        "runtime_seconds": time.time() - started,
    }
    (outputs / "results-summary.json").write_text(json.dumps(json_safe(summary), indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    (work / "runtime-provenance.json").write_text(json.dumps({"seed": seed, "frame_n": args.n, "snr_grid_db": list(np.arange(8.0, 20.01, 0.5)), "fft_length": args.n, "normalization": "numpy default fft/ifft", "window": "none", "zero_padding": False, "main_ber_threshold": target, "channel_order": "dispersion -> phase noise -> AWGN -> inverse dispersion -> CR"}, indent=2), encoding="utf-8")
    print(json.dumps({"baseline_rsnr_db": baseline_snr, "q1_primary": q1_primary, "q3_best": q3_best, "q4_best": q4_best, "synthetic_status": synth["status"], "runtime_seconds": summary["runtime_seconds"]}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
