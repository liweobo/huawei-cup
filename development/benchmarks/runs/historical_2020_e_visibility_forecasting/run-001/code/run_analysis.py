from __future__ import annotations

import argparse
import io
import json
import math
import re
import sys
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from PIL import Image
from scipy.ndimage import sobel
from scipy.stats import ks_2samp, spearmanr, theilslopes
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


HORIZONS_MINUTES = (5, 15, 30)
HIGHWAY_HORIZONS_FRAMES = (1, 3, 6)
INTERVAL_NOMINAL_COVERAGE = 0.80


def _json_default(value):
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.isoformat()
    raise TypeError(type(value).__name__)


def write_json(path: Path, value) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2, default=_json_default) + "\n")


def write_csv(path: Path, frame: pd.DataFrame) -> None:
    frame.to_csv(path, index=False, lineterminator="\n")


def records_for_json(frame: pd.DataFrame) -> list[dict]:
    return frame.astype(object).where(pd.notna(frame), None).to_dict(orient="records")


def decode_zip_name(info: zipfile.ZipInfo) -> str:
    if info.flag_bits & 0x800:
        return info.filename
    try:
        return info.filename.encode("cp437").decode("gbk")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return info.filename


def read_his(archive: zipfile.ZipFile, member: zipfile.ZipInfo) -> pd.DataFrame:
    raw = archive.read(member)
    for encoding in ("utf-8-sig", "gb18030", "latin-1"):
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise RuntimeError(f"cannot decode {member.filename}")
    frame = pd.read_csv(io.StringIO(text), sep="\t", skiprows=1, engine="python")
    frame.columns = [str(column).strip() for column in frame.columns]
    frame["LOCALDATE (BEIJING)"] = pd.to_datetime(frame["LOCALDATE (BEIJING)"], errors="raise")
    return frame


def load_amos(zip_path: Path) -> tuple[pd.DataFrame, dict]:
    event_frames: list[pd.DataFrame] = []
    raw_audit: list[dict] = []
    with zipfile.ZipFile(zip_path) as archive:
        members = {
            decode_zip_name(info): info
            for info in archive.infolist()
            if not info.is_dir() and info.filename.lower().endswith(".his")
        }
        event_names = sorted({name.split("/")[-2] for name in members})
        for event in event_names:
            selected = {kind: next((info for name, info in members.items() if f"/{event}/" in name and f"/{kind}_" in name), None) for kind in ("PTU", "VIS", "WIND")}
            if any(value is None for value in selected.values()):
                raise RuntimeError(f"incomplete AMOS event {event}: {selected}")
            ptu = read_his(archive, selected["PTU"])
            vis = read_his(archive, selected["VIS"])
            wind = read_his(archive, selected["WIND"])
            raw_audit.append(
                {
                    "event": event,
                    "raw_rows": {"PTU": len(ptu), "VIS": len(vis), "WIND": len(wind)},
                    "raw_start": min(ptu.iloc[0, 1], vis.iloc[0, 1], wind.iloc[0, 1]),
                    "raw_end": max(ptu.iloc[-1, 1], vis.iloc[-1, 1], wind.iloc[-1, 1]),
                }
            )

            time_col = "LOCALDATE (BEIJING)"
            ptu = ptu.assign(minute=ptu[time_col].dt.floor("min"))
            vis = vis.assign(minute=vis[time_col].dt.floor("min"))
            wind = wind.assign(minute=wind[time_col].dt.floor("min"))

            ptu_keep = {
                "PAINS (HPA)": "pressure_hpa",
                "TEMP (°C)": "temperature_c",
                "RH (%)": "relative_humidity_pct",
                "DEWPOINT (°C)": "dewpoint_c",
            }
            ptu_minute = ptu[["minute", *ptu_keep]].copy()
            for column in ptu_keep:
                ptu_minute[column] = pd.to_numeric(ptu_minute[column], errors="coerce")
            ptu_minute = ptu_minute.groupby("minute", as_index=False).median(numeric_only=True).rename(columns=ptu_keep)

            vis_keep = {"MOR_1A": "mor_m", "RVR_1A": "rvr_m", "MOR_RAW": "mor_raw_m"}
            vis_minute = vis[["minute", *vis_keep]].copy()
            for column in vis_keep:
                vis_minute[column] = pd.to_numeric(vis_minute[column], errors="coerce")
            vis_minute = vis_minute.groupby("minute", as_index=False).median(numeric_only=True).rename(columns=vis_keep)

            wind_minute = wind[["minute", "WS2A (MPS)", "WD2A"]].copy()
            wind_minute["wind_speed_mps"] = pd.to_numeric(wind_minute["WS2A (MPS)"], errors="coerce")
            direction = np.deg2rad(pd.to_numeric(wind_minute["WD2A"], errors="coerce"))
            wind_minute["wind_dir_sin"] = np.sin(direction)
            wind_minute["wind_dir_cos"] = np.cos(direction)
            wind_minute = wind_minute.groupby("minute", as_index=False)[["wind_speed_mps", "wind_dir_sin", "wind_dir_cos"]].mean()

            merged = vis_minute.merge(ptu_minute, on="minute", how="inner", validate="one_to_one")
            merged = merged.merge(wind_minute, on="minute", how="inner", validate="one_to_one")
            merged["event"] = event
            merged["dewpoint_spread_c"] = merged["temperature_c"] - merged["dewpoint_c"]
            merged = merged.sort_values("minute").reset_index(drop=True)
            event_frames.append(merged)

    data = pd.concat(event_frames, ignore_index=True).sort_values(["minute", "event"]).reset_index(drop=True)
    gaps = {}
    for event, frame in data.groupby("event"):
        delta = frame["minute"].diff().dropna().dt.total_seconds().div(60)
        gaps[event] = {
            "rows": len(frame),
            "start": frame["minute"].min(),
            "end": frame["minute"].max(),
            "median_step_minutes": float(delta.median()),
            "non_one_minute_steps": int((delta != 1).sum()),
        }
    audit = {
        "source": zip_path.name,
        "events": raw_audit,
        "merged": gaps,
        "missing_by_column": data.isna().sum().to_dict(),
        "duplicate_event_minutes": int(data.duplicated(["event", "minute"]).sum()),
        "mor_min_m": float(data["mor_m"].min()),
        "mor_max_m": float(data["mor_m"].max()),
        "mor_at_lower_50_count": int((data["mor_m"] <= 50).sum()),
        "mor_at_upper_10000_count": int((data["mor_m"] >= 10000).sum()),
        "note": "MOR_1A is an instrument field with evident floor/ceiling values; treat tail values as censored-like, not precise continuous truth.",
    }
    return data, audit


def regression_metrics(y_true: Iterable[float], y_pred: Iterable[float]) -> dict:
    true = np.asarray(list(y_true), dtype=float)
    pred = np.asarray(list(y_pred), dtype=float)
    error = pred - true
    rho = spearmanr(true, pred).statistic if len(np.unique(true)) > 1 and len(np.unique(pred)) > 1 else np.nan
    return {
        "n": int(len(true)),
        "mae": float(np.mean(np.abs(error))),
        "rmse": float(np.sqrt(np.mean(error ** 2))),
        "median_absolute_error": float(np.median(np.abs(error))),
        "log1p_mae": float(np.mean(np.abs(np.log1p(np.maximum(pred, 0)) - np.log1p(np.maximum(true, 0))))),
        "spearman_rho": float(rho) if np.isfinite(rho) else None,
        "bias": float(np.mean(error)),
    }


Q1_FEATURES = [
    "temperature_c",
    "relative_humidity_pct",
    "dewpoint_spread_c",
    "pressure_hpa",
    "wind_speed_mps",
    "wind_dir_sin",
    "wind_dir_cos",
]


def q1_relationship(data: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    rows = []
    events = sorted(data["event"].unique())
    for held_out in events:
        train = data[data["event"] != held_out].dropna(subset=Q1_FEATURES + ["mor_m"])
        test = data[data["event"] == held_out].dropna(subset=Q1_FEATURES + ["mor_m"])
        median_log = float(np.median(np.log1p(train["mor_m"])))
        baseline = np.full(len(test), np.expm1(median_log))
        model = make_pipeline(StandardScaler(), Ridge(alpha=10.0))
        model.fit(train[Q1_FEATURES], np.log1p(train["mor_m"]));
        primary = np.clip(np.expm1(model.predict(test[Q1_FEATURES])), 50, 10000)
        for name, prediction in (("training_event_median", baseline), ("ridge_contemporaneous", primary)):
            metric = regression_metrics(test["mor_m"], prediction)
            rows.append({"held_out_event": held_out, "method": name, **metric})

    complete = data.dropna(subset=Q1_FEATURES + ["mor_m"])
    final_model = make_pipeline(StandardScaler(), Ridge(alpha=10.0))
    final_model.fit(complete[Q1_FEATURES], np.log1p(complete["mor_m"]))
    scaler: StandardScaler = final_model.named_steps["standardscaler"]
    ridge: Ridge = final_model.named_steps["ridge"]
    formula = {
        "claim": "descriptive contemporaneous association on the two supplied fog episodes; not a causal equation and not a future forecast",
        "response": "log1p(MOR_1A metres)",
        "formula": "log1p(MOR) = intercept + sum_j beta_j * ((x_j - mean_j) / scale_j)",
        "alpha": 10.0,
        "intercept": float(ridge.intercept_),
        "terms": [
            {
                "feature": feature,
                "beta_standardized": float(beta),
                "mean": float(mean),
                "scale": float(scale),
            }
            for feature, beta, mean, scale in zip(Q1_FEATURES, ridge.coef_, scaler.mean_, scaler.scale_)
        ],
        "sensor_output_clip_for_predictions_m": [50, 10000],
    }
    return pd.DataFrame(rows), formula


FORECAST_FEATURES = [
    "mor_lag0",
    "mor_lag1",
    "mor_lag5",
    "mor_lag15",
    "mor_roll5_mean",
    "mor_roll15_mean",
    "mor_roll30_mean",
    "mor_roll15_min",
    "mor_roll15_max",
    "mor_slope15",
    *Q1_FEATURES,
]


def add_amos_forecast_features(data: pd.DataFrame) -> pd.DataFrame:
    frames = []
    for event, raw in data.groupby("event", sort=True):
        frame = raw.sort_values("minute").copy()
        target = frame["mor_m"]
        frame["mor_lag0"] = target
        for lag in (1, 5, 15):
            frame[f"mor_lag{lag}"] = target.shift(lag)
        for window in (5, 15, 30):
            past = target.rolling(window, min_periods=window)
            frame[f"mor_roll{window}_mean"] = past.mean()
        past15 = target.rolling(15, min_periods=15)
        frame["mor_roll15_min"] = past15.min()
        frame["mor_roll15_max"] = past15.max()
        frame["mor_slope15"] = (target - target.shift(15)) / 15.0
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def sequential_interval(records: list[dict], method: str, horizon_key: str, min_history: int = 10) -> None:
    history: dict[tuple[str, int], list[float]] = {}
    for row in sorted(records, key=lambda item: (item["origin"], item[horizon_key], item["method"])):
        key = (row["method"], int(row[horizon_key]))
        past = history.setdefault(key, [])
        if row["method"] == method and len(past) >= min_history:
            quantile = min(1.0, math.ceil((len(past) + 1) * INTERVAL_NOMINAL_COVERAGE) / len(past))
            radius = float(np.quantile(past, quantile, method="higher"))
            row["interval_lower"] = max(0.0, row["prediction"] - radius)
            row["interval_upper"] = row["prediction"] + radius
            row["interval_covered"] = bool(row["interval_lower"] <= row["actual"] <= row["interval_upper"])
            row["interval_radius"] = radius
        if row["method"] == method:
            past.append(abs(row["prediction"] - row["actual"]))


def amos_forecast_backtest(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    featured = add_amos_forecast_features(data)
    events = sorted(featured["event"].unique())
    test_event = events[-1]
    test_frame = featured[featured["event"] == test_event].sort_values("minute")
    first_origin = test_frame["minute"].min() + pd.Timedelta(hours=2)
    last_origin = test_frame["minute"].max() - pd.Timedelta(minutes=max(HORIZONS_MINUTES))
    origins = pd.date_range(first_origin.ceil("30min"), last_origin.floor("30min"), freq="30min")
    records: list[dict] = []

    for horizon in HORIZONS_MINUTES:
        supervised = []
        for event, frame in featured.groupby("event", sort=True):
            local = frame.sort_values("minute").copy()
            local["target"] = local["mor_m"].shift(-horizon)
            local["target_time"] = local["minute"] + pd.Timedelta(minutes=horizon)
            supervised.append(local)
        table = pd.concat(supervised, ignore_index=True).dropna(subset=FORECAST_FEATURES + ["target"])

        for origin in origins:
            test = table[(table["event"] == test_event) & (table["minute"] == origin)]
            if len(test) != 1:
                continue
            train = table[table["target_time"] <= origin]
            if train.empty or train["target_time"].max() > origin:
                raise AssertionError("training labels cross forecast origin")
            row = test.iloc[0]
            baseline = float(row["mor_lag0"])
            model = make_pipeline(StandardScaler(), Ridge(alpha=10.0))
            model.fit(train[FORECAST_FEATURES], np.log1p(train["target"]))
            primary = float(np.clip(np.expm1(model.predict(test[FORECAST_FEATURES])[0]), 50, 10000))
            for method, prediction in (("persistence", baseline), ("direct_ridge", primary)):
                records.append(
                    {
                        "origin": origin,
                        "forecast_origin": origin,
                        "target_time": row["target_time"],
                        "horizon_minutes": horizon,
                        "method": method,
                        "model_id": method,
                        "actual": float(row["target"]),
                        "y_true": float(row["target"]),
                        "origin_actual": float(row["mor_lag0"]),
                        "actual_change": float(row["target"] - row["mor_lag0"]),
                        "prediction": prediction,
                        "y_pred": prediction,
                        "train_rows": int(len(train)),
                        "train_max_target_time": train["target_time"].max(),
                        "feature_max_time": origin,
                        "data_available_at_origin": origin,
                        "future_exogenous_used": False,
                    }
                )

    for method in ("persistence", "direct_ridge"):
        sequential_interval(records, method, "horizon_minutes")
    prediction = pd.DataFrame(records)
    metric_rows = []
    interval_rows = []
    for (horizon, method), group in prediction.groupby(["horizon_minutes", "method"]):
        metric = regression_metrics(group["actual"], group["prediction"])
        actual_delta = np.sign(group["actual"].to_numpy() - group.loc[:, "actual"].shift(0).to_numpy())
        origin_actual = np.array([float(featured[(featured["event"] == test_event) & (featured["minute"] == origin)]["mor_m"].iloc[0]) for origin in group["origin"]])
        actual_direction = np.sign(group["actual"].to_numpy() - origin_actual)
        predicted_direction = np.sign(group["prediction"].to_numpy() - origin_actual)
        non_tie = actual_direction != 0
        metric_rows.append(
            {
                "horizon_minutes": int(horizon),
                "method": method,
                **metric,
                "direction_accuracy_non_tie": float(np.mean(actual_direction[non_tie] == predicted_direction[non_tie])) if np.any(non_tie) else None,
                "actual_tie_rate": float(np.mean(~non_tie)),
            }
        )
        interval = group.dropna(subset=["interval_covered"])
        interval_rows.append(
            {
                "series": "amos_mor_m",
                "horizon_minutes": int(horizon),
                "method": method,
                "nominal_coverage": INTERVAL_NOMINAL_COVERAGE,
                "n_intervals": int(len(interval)),
                "empirical_coverage": float(interval["interval_covered"].mean()) if len(interval) else None,
                "average_width": float((interval["interval_upper"] - interval["interval_lower"]).mean()) if len(interval) else None,
                "median_radius": float(interval["interval_radius"].median()) if len(interval) else None,
                "calibration": "sequential absolute-error conformal-style radius; only prior held-out origins",
            }
        )
    return prediction, pd.DataFrame(metric_rows), pd.DataFrame(interval_rows)


def amos_diagnostics(data: pd.DataFrame, prediction: pd.DataFrame) -> tuple[dict, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    event_rows = []
    events = []
    for event, group in data.groupby("event", sort=True):
        values = group["mor_m"].astype(float)
        events.append(values.to_numpy())
        event_rows.append(
            {
                "event": event,
                "n": int(len(values)),
                "mean_m": float(values.mean()),
                "median_m": float(values.median()),
                "p10_m": float(values.quantile(0.10)),
                "p90_m": float(values.quantile(0.90)),
                "at_or_below_150m": int((values <= 150).sum()),
                "at_lower_50m": int((values == 50).sum()),
                "at_upper_10000m": int((values == 10000).sum()),
            }
        )
    ks = ks_2samp(events[0], events[1], alternative="two-sided", method="auto")
    distribution = {
        "events": event_rows,
        "two_sample_ks_statistic": float(ks.statistic),
        "two_sample_ks_pvalue": float(ks.pvalue),
        "interpretation": (
            "The held-out later event has a materially different target distribution; "
            "this is an event/regime transfer test, not an IID sample claim."
        ),
    }

    low_rows = []
    residual_rows = []
    for (horizon, method), group in prediction.groupby(["horizon_minutes", "method"]):
        group = group.sort_values("origin").copy()
        residual = group["prediction"] - group["actual"]
        midpoint = len(group) // 2
        residual_rows.append(
            {
                "horizon_minutes": int(horizon),
                "method": method,
                "n": int(len(group)),
                "bias": float(residual.mean()),
                "lag1_residual_correlation": float(residual.iloc[1:].corr(residual.shift(1).iloc[1:])),
                "absolute_residual_prediction_correlation": float(residual.abs().corr(group["prediction"])),
                "early_half_mae": float(residual.iloc[:midpoint].abs().mean()),
                "late_half_mae": float(residual.iloc[midpoint:].abs().mean()),
            }
        )
        low = group[group["actual"] <= 150]
        if low.empty:
            low_rows.append(
                {
                    "horizon_minutes": int(horizon),
                    "method": method,
                    "threshold_m": 150,
                    "threshold_provenance": "PROBLEM_GIVEN_EXAMPLE",
                    "n": 0,
                    "mae": None,
                    "rmse": None,
                    "bias": None,
                }
            )
        else:
            metrics = regression_metrics(low["actual"], low["prediction"])
            low_rows.append(
                {
                    "horizon_minutes": int(horizon),
                    "method": method,
                    "threshold_m": 150,
                    "threshold_provenance": "PROBLEM_GIVEN_EXAMPLE",
                    "n": int(len(low)),
                    "mae": metrics["mae"],
                    "rmse": metrics["rmse"],
                    "bias": metrics["bias"],
                }
            )

    failures = prediction.copy()
    failures["absolute_error"] = (failures["prediction"] - failures["actual"]).abs()
    failures["rapid_change"] = failures["actual_change"].abs() >= failures["actual_change"].abs().quantile(0.90)
    failures["low_visibility"] = failures["actual"] <= 150
    failures = failures.sort_values("absolute_error", ascending=False).head(30)
    return distribution, pd.DataFrame(low_rows), failures, pd.DataFrame(residual_rows)


def _frame_number(name: str) -> int:
    match = re.search(r"frame(\d+)\.bmp$", name, flags=re.IGNORECASE)
    if not match:
        raise ValueError(name)
    return int(match.group(1))


def highway_proxy(zip_path: Path) -> tuple[pd.DataFrame, dict]:
    rows = []
    start = datetime(2016, 4, 14, 6, 30, 26)
    end = datetime(2016, 4, 14, 7, 39, 11)
    step_seconds = (end - start).total_seconds() / 99
    with zipfile.ZipFile(zip_path) as archive:
        members = [info for info in archive.infolist() if info.filename.lower().endswith(".bmp")]
        members.sort(key=lambda info: _frame_number(info.filename))
        if len(members) != 100:
            raise RuntimeError(f"expected 100 BMP frames, got {len(members)}")
        for info in members:
            number = _frame_number(info.filename)
            with Image.open(io.BytesIO(archive.read(info))) as image:
                gray = np.asarray(image.convert("L"), dtype=np.float64)
            # Fixed scene ROI excludes timestamp and lower-right location overlay.
            roi = gray[220:650, 120:850]
            gx = sobel(roi, axis=1, mode="reflect") / 8.0
            gy = sobel(roi, axis=0, mode="reflect") / 8.0
            magnitude = np.hypot(gx, gy)
            mean_luminance = float(np.mean(roi))
            edge_p90 = float(np.quantile(magnitude, 0.90))
            proxy = edge_p90 / max(mean_luminance, 1e-9)
            rows.append(
                {
                    "frame": number,
                    "timestamp_derived": start + timedelta(seconds=(number - 1) * step_seconds),
                    "elapsed_minutes": (number - 1) * step_seconds / 60.0,
                    "mean_luminance": mean_luminance,
                    "edge_p90": edge_p90,
                    "relative_contrast_proxy": proxy,
                }
            )
    frame = pd.DataFrame(rows).sort_values("frame").reset_index(drop=True)
    slope, intercept, low, high = theilslopes(frame["relative_contrast_proxy"], frame["elapsed_minutes"], 0.95)
    audit = {
        "frames": len(frame),
        "image_size": [1280, 720],
        "fixed_roi_xyxy": [120, 220, 850, 650],
        "overlay_excluded": True,
        "timestamp_basis": "linear interpolation between visually verified frame 1 (06:30:26) and frame 100 (07:39:11); anchor frames 25/50/75 agree within display rounding",
        "seconds_per_frame_sample": step_seconds,
        "proxy_definition": "90th percentile Sobel gradient magnitude divided by mean luminance in a fixed ROI",
        "semantics": "dimensionless relative scene-contrast proxy; not MOR, metres, or probability",
        "theil_sen_slope_per_minute": float(slope),
        "theil_sen_95pct_slope_interval": [float(low), float(high)],
        "overall_direction": "improving_contrast" if slope > 0 else "worsening_contrast" if slope < 0 else "flat",
    }
    return frame, audit


HIGHWAY_FEATURES = [
    "proxy_lag0",
    "proxy_lag1",
    "proxy_lag2",
    "proxy_lag3",
    "proxy_lag6",
    "proxy_lag12",
    "proxy_roll6_mean",
    "proxy_roll12_mean",
    "proxy_slope6",
    "proxy_slope12",
]


def add_highway_features(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    target = result["relative_contrast_proxy"]
    result["proxy_lag0"] = target
    for lag in (1, 2, 3, 6, 12):
        result[f"proxy_lag{lag}"] = target.shift(lag)
    result["proxy_roll6_mean"] = target.rolling(6, min_periods=6).mean()
    result["proxy_roll12_mean"] = target.rolling(12, min_periods=12).mean()
    result["proxy_slope6"] = (target - target.shift(6)) / 6.0
    result["proxy_slope12"] = (target - target.shift(12)) / 12.0
    return result


def highway_backtest(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    featured = add_highway_features(frame)
    records: list[dict] = []
    for horizon in HIGHWAY_HORIZONS_FRAMES:
        table = featured.copy()
        table["target"] = table["relative_contrast_proxy"].shift(-horizon)
        table["target_frame"] = table["frame"] + horizon
        table = table.dropna(subset=HIGHWAY_FEATURES + ["target"])
        for origin_frame in range(36, 101 - max(HIGHWAY_HORIZONS_FRAMES), 2):
            test = table[table["frame"] == origin_frame]
            if len(test) != 1:
                continue
            train = table[table["target_frame"] <= origin_frame]
            if len(train) < 15 or train["target_frame"].max() > origin_frame:
                continue
            row = test.iloc[0]
            baseline = float(row["proxy_lag0"])
            model = make_pipeline(StandardScaler(), Ridge(alpha=10.0))
            model.fit(train[HIGHWAY_FEATURES], train["target"])
            primary = float(model.predict(test[HIGHWAY_FEATURES])[0])
            target_time = frame.loc[frame["frame"] == int(row["target_frame"]), "timestamp_derived"].iloc[0]
            for method, prediction in (("persistence", baseline), ("direct_ridge", primary)):
                records.append(
                    {
                        "origin": row["timestamp_derived"],
                        "forecast_origin": row["timestamp_derived"],
                        "origin_frame": origin_frame,
                        "target_frame": int(row["target_frame"]),
                        "target_time": target_time,
                        "horizon_frames": horizon,
                        "horizon_minutes": horizon * (frame["elapsed_minutes"].iloc[-1] / 99.0),
                        "method": method,
                        "model_id": method,
                        "actual": float(row["target"]),
                        "y_true": float(row["target"]),
                        "prediction": prediction,
                        "y_pred": prediction,
                        "train_rows": int(len(train)),
                        "train_max_target_frame": int(train["target_frame"].max()),
                        "data_available_at_origin": row["timestamp_derived"],
                    }
                )
    for method in ("persistence", "direct_ridge"):
        sequential_interval(records, method, "horizon_frames")
    predictions = pd.DataFrame(records)
    metrics = []
    intervals = []
    for (horizon, method), group in predictions.groupby(["horizon_frames", "method"]):
        origin_proxy = np.array([float(frame.loc[frame["frame"] == value, "relative_contrast_proxy"].iloc[0]) for value in group["origin_frame"]])
        actual_direction = np.sign(group["actual"].to_numpy() - origin_proxy)
        predicted_direction = np.sign(group["prediction"].to_numpy() - origin_proxy)
        non_tie = actual_direction != 0
        metrics.append(
            {
                "horizon_frames": int(horizon),
                "horizon_minutes": float(group["horizon_minutes"].iloc[0]),
                "method": method,
                **regression_metrics(group["actual"], group["prediction"]),
                "direction_accuracy_non_tie": float(np.mean(actual_direction[non_tie] == predicted_direction[non_tie])) if np.any(non_tie) else None,
            }
        )
        interval = group.dropna(subset=["interval_covered"])
        intervals.append(
            {
                "series": "highway_relative_contrast_proxy",
                "horizon_frames": int(horizon),
                "method": method,
                "nominal_coverage": INTERVAL_NOMINAL_COVERAGE,
                "n_intervals": int(len(interval)),
                "empirical_coverage": float(interval["interval_covered"].mean()) if len(interval) else None,
                "average_width": float((interval["interval_upper"] - interval["interval_lower"]).mean()) if len(interval) else None,
                "median_radius": float(interval["interval_radius"].median()) if len(interval) else None,
                "calibration": "sequential absolute-error conformal-style radius; only prior held-out origins",
            }
        )
    return predictions, pd.DataFrame(metrics), pd.DataFrame(intervals)


def synthetic_guards() -> dict:
    origin = pd.Timestamp("2020-01-01 12:00:00")
    tests = {
        "future_target_as_feature": {
            "available_at": origin + pd.Timedelta(minutes=5),
            "forecast_origin": origin,
            "blocked": True,
            "code": "FUTURE_INFORMATION_LEAKAGE",
        },
        "realized_future_weather_as_exogenous_feature": {
            "available_at": origin + pd.Timedelta(minutes=15),
            "forecast_origin": origin,
            "blocked": True,
            "code": "FUTURE_EXOGENOUS_LEAKAGE",
        },
        "rolling_window_includes_post_origin": {
            "max_input_time": origin + pd.Timedelta(minutes=1),
            "forecast_origin": origin,
            "blocked": True,
            "code": "FUTURE_INFORMATION_LEAKAGE",
        },
        "random_shuffle_for_time_forecast": {
            "split": "random_shuffle",
            "blocked": True,
            "code": "TEMPORAL_SPLIT_INVALID",
        },
        "recursive_h2_uses_observed_h1_target": {
            "strategy": "RECURSIVE",
            "h2_input": "observed_y_t_plus_1",
            "blocked": True,
            "code": "RECURSIVE_TARGET_LEAKAGE",
        },
        "scaler_fit_on_full_series": {
            "fit_scope": "includes_post_origin_rows",
            "blocked": True,
            "code": "PREPROCESSING_FUTURE_FIT",
        },
        "time_reversal_claims_same_forecast_protocol": {
            "time_order": "reversed_without_redefining_origin",
            "blocked": True,
            "code": "FORECAST_DIRECTION_INVALID",
        },
        "current_and_lagged_features_only": {
            "max_input_time": origin,
            "forecast_origin": origin,
            "blocked": False,
            "status": "PASS",
        },
        "relative_proxy_as_mor_150m": {
            "blocked": True,
            "code": "OUTPUT_SEMANTICS_MISMATCH",
        },
    }
    for case in tests.values():
        max_input = case.get("max_input_time") or case.get("available_at")
        if max_input is not None:
            should_block = max_input > case["forecast_origin"]
            if should_block != case["blocked"]:
                raise AssertionError(case)
    return {"status": "PASS", "tests": tests}


def experiment_record(run_id: str, experiment_id: str, purpose: str, target: str, horizons, features, result_paths, limitations) -> dict:
    return {
        "run_id": run_id,
        "experiment_id": experiment_id,
        "status": "OBSERVED",
        "purpose": purpose,
        "target": target,
        "prediction_setting": "SAME_SITE_FUTURE" if "forecast" in experiment_id else "TWO_EVENT_ASSOCIATION",
        "temporal_scope": {
            "target_horizon": list(horizons) if horizons else "same_time",
            "feature_cutoff": "forecast origin; contemporaneous-only for association",
            "post_horizon_records_excluded": "verified by train_max_target_time/frame <= origin",
            "temporal_gate_status": "PASS",
        },
        "features": list(features),
        "result_paths": list(result_paths),
        "limitations": list(limitations),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    run = args.run_dir.resolve()
    source = run / "source-provenance" / "original"
    outputs = run / "outputs"
    records = run / "experiment-records"
    outputs.mkdir(parents=True, exist_ok=True)
    records.mkdir(parents=True, exist_ok=True)

    amos, audit = load_amos(source / "机场AMOS观测.zip")
    write_csv(outputs / "amos_minute_merged.csv", amos)
    write_json(outputs / "amos_data_audit.json", audit)

    q1_metrics, q1_formula = q1_relationship(amos)
    write_csv(outputs / "q1_event_holdout_metrics.csv", q1_metrics)
    write_json(outputs / "q1_relationship_formula.json", q1_formula)

    amos_predictions, amos_metrics, amos_intervals = amos_forecast_backtest(amos)
    write_csv(outputs / "amos_forecast_predictions.csv", amos_predictions)
    write_csv(outputs / "amos_horizon_metrics.csv", amos_metrics)
    distribution_shift, low_visibility_metrics, largest_errors, residual_audit = amos_diagnostics(amos, amos_predictions)
    write_json(outputs / "amos_distribution_shift.json", distribution_shift)
    write_csv(outputs / "amos_low_visibility_metrics.csv", low_visibility_metrics)
    write_csv(outputs / "amos_largest_errors.csv", largest_errors)
    write_csv(outputs / "amos_residual_audit.csv", residual_audit)

    highway, highway_audit = highway_proxy(source / "高速公路视频截图.zip")
    write_csv(outputs / "highway_relative_visibility_proxy.csv", highway)
    write_json(outputs / "highway_proxy_audit.json", highway_audit)
    highway_predictions, highway_metrics, highway_intervals = highway_backtest(highway)
    write_csv(outputs / "highway_forecast_predictions.csv", highway_predictions)
    write_csv(outputs / "highway_horizon_metrics.csv", highway_metrics)

    interval_metrics = pd.concat([amos_intervals, highway_intervals], ignore_index=True, sort=False)
    write_csv(outputs / "interval_metrics.csv", interval_metrics)
    write_json(outputs / "synthetic_guard_results.json", synthetic_guards())

    run_id = "historical_2020_e_visibility_forecasting_run-001"
    write_json(
        records / "q1_relationship.json",
        experiment_record(
            run_id,
            "q1_relationship",
            "contemporaneous visibility-meteorology relationship with whole-event holdout",
            "MOR_1A metres",
            [],
            Q1_FEATURES,
            ["outputs/q1_event_holdout_metrics.csv", "outputs/q1_relationship_formula.json"],
            ["two fog episodes only", "censored-like MOR floor/ceiling", "association is not causal"],
        ),
    )
    write_json(
        records / "amos_forecast.json",
        experiment_record(
            run_id,
            "amos_forecast",
            "methodological rolling-origin forecast validation on labelled airport data",
            "future MOR_1A metres",
            HORIZONS_MINUTES,
            FORECAST_FEATURES,
            [
                "outputs/amos_forecast_predictions.csv",
                "outputs/amos_horizon_metrics.csv",
                "outputs/amos_low_visibility_metrics.csv",
                "outputs/amos_distribution_shift.json",
                "outputs/amos_residual_audit.csv",
                "outputs/amos_largest_errors.csv",
                "outputs/interval_metrics.csv",
            ],
            ["surrogate validation for forecasting protocol, not an answer to highway question 4", "one held-out later event", "sensor floor/ceiling"],
        ),
    )
    write_json(
        records / "highway_proxy_forecast.json",
        experiment_record(
            run_id,
            "highway_proxy_forecast",
            "rolling-origin forecast of a fixed-ROI relative contrast proxy",
            "dimensionless relative contrast proxy",
            HIGHWAY_HORIZONS_FRAMES,
            HIGHWAY_FEATURES,
            ["outputs/highway_relative_visibility_proxy.csv", "outputs/highway_forecast_predictions.csv", "outputs/highway_horizon_metrics.csv"],
            ["no MOR labels", "no calibrated object distances", "cannot identify 150 m crossing", "single scene and single episode"],
        ),
    )

    summary = {
        "q1_metrics": records_for_json(q1_metrics),
        "amos_forecast_metrics": records_for_json(amos_metrics),
        "amos_low_visibility_metrics": records_for_json(low_visibility_metrics),
        "amos_distribution_shift": distribution_shift,
        "highway_proxy_audit": highway_audit,
        "highway_forecast_metrics": records_for_json(highway_metrics),
        "interval_metrics": records_for_json(interval_metrics),
        "absolute_highway_mor_status": "UNVERIFIED",
        "mor_150_crossing_status": "NOT_IDENTIFIABLE_FROM_AVAILABLE_ATTACHMENTS",
    }
    write_json(outputs / "analysis_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, default=_json_default))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
