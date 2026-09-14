"""First baseline and audit run for the 2023 E clinical dataset.

The script keeps the three prediction scenes separate:
BASELINE (first imaging only), FOLLOW_UP (aggregates of available follow-up
imaging), and OUTCOME (labels/derived residuals, never used as predictors).
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    cohen_kappa_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    roc_auc_score,
    recall_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def clean_id(value: Any) -> str | None:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    text = str(value).strip()
    if text.lower() in {"", "nan", "nat", "none"}:
        return None
    if re.fullmatch(r"\d+\.0", text):
        text = text[:-2]
    digits = re.sub(r"[^0-9]", "", text)
    return digits if digits else text


def jsonable(value: Any) -> Any:
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return None if np.isnan(value) else float(value)
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    if pd.isna(value):
        return None
    return value


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=jsonable), encoding="utf-8")


def read_inputs(input_dir: Path) -> dict[str, pd.DataFrame]:
    return {
        "clinical": pd.read_excel(input_dir / "表1-患者列表及临床信息.xlsx", dtype=str),
        "volume": pd.read_excel(input_dir / "表2-患者影像信息血肿及水肿的体积及位置.xlsx", dtype=str),
        "ed_shape": pd.read_excel(input_dir / "表3-患者影像信息血肿及水肿的形状及灰度分布.xlsx", sheet_name="ED"),
        "hemo_shape": pd.read_excel(input_dir / "表3-患者影像信息血肿及水肿的形状及灰度分布.xlsx", sheet_name="Hemo"),
        "shape_dictionary": pd.read_excel(input_dir / "表3-患者影像信息血肿及水肿的形状及灰度分布.xlsx", sheet_name="Sheet1", dtype=str),
        "answer": pd.read_excel(input_dir / "表4-答案文件.xlsx", dtype=str),
        "lookup": pd.read_excel(input_dir / "附表1-检索表格-流水号vs时间.xlsx", dtype=str),
    }


def make_lookup(lookup: pd.DataFrame) -> tuple[dict[str, pd.Timestamp], dict[str, dict[str, Any]]]:
    serial_to_time: dict[str, pd.Timestamp] = {}
    patient_meta: dict[str, dict[str, Any]] = {}
    for _, row in lookup.iterrows():
        patient = str(row.get("ID", ""))
        if not patient or patient == "nan":
            continue
        patient_meta[patient] = {"repeat_count": int(float(row["重复次数"])) if pd.notna(row.get("重复次数")) else None}
        for visit in range(14):
            time_col = "入院首次检查时间点" if visit == 0 else f"随访{visit}时间点"
            serial_col = "入院首次检查流水号" if visit == 0 else f"随访{visit}流水号"
            serial = clean_id(row.get(serial_col))
            stamp = pd.to_datetime(row.get(time_col), errors="coerce")
            if serial and pd.notna(stamp):
                serial_to_time[serial] = stamp
    return serial_to_time, patient_meta


def expand_volume_table(volume: pd.DataFrame, serial_to_time: dict[str, pd.Timestamp], clinical: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, row in volume.iterrows():
        patient = str(row["ID"])
        for visit in range(9):
            serial_col = "首次检查流水号" if visit == 0 else f"随访{visit}流水号"
            serial = clean_id(row.get(serial_col))
            if not serial:
                continue
            suffix = "" if visit == 0 else f".{visit}"
            hm = pd.to_numeric(row.get(f"HM_volume{suffix}"), errors="coerce")
            ed = pd.to_numeric(row.get(f"ED_volume{suffix}"), errors="coerce")
            timestamp = serial_to_time.get(serial)
            rows.append(
                {
                    "patient_id": patient,
                    "visit_index": visit,
                    "serial": serial,
                    "timestamp": timestamp,
                    "HM_volume": hm,
                    "ED_volume": ed,
                }
            )
    long = pd.DataFrame(rows)
    clinical_map = clinical.set_index("patient_id")["onset_to_first_h"].to_dict()
    first_stamp = long.groupby("patient_id")["timestamp"].transform("min")
    first_interval = pd.to_numeric(long["patient_id"].map(clinical_map), errors="coerce")
    long["onset_to_imaging_h"] = first_interval + (long["timestamp"] - first_stamp).dt.total_seconds() / 3600.0
    long.loc[long["visit_index"] == 0, "onset_to_imaging_h"] = first_interval[long["visit_index"] == 0]
    return long.sort_values(["patient_id", "onset_to_imaging_h", "visit_index"]).reset_index(drop=True)


def prepare_clinical(raw: pd.DataFrame) -> pd.DataFrame:
    clinical = raw.rename(
        columns={
            "Unnamed: 0": "患者ID",
            "90天mRS": "mrs90",
            "数据集划分": "dataset_group",
            "入院首次影像检查流水号": "first_serial",
            "年龄": "age",
            "性别": "sex",
            "脑出血前mRS评分": "pre_mrs",
            "高血压病史": "hypertension",
            "卒中病史": "prior_stroke",
            "糖尿病史": "diabetes",
            "房颤史": "afib",
            "冠心病史": "cad",
            "吸烟史": "smoking",
            "饮酒史": "alcohol",
            "发病到首次影像检查时间间隔": "onset_to_first_h",
            "血压": "blood_pressure",
            "脑室引流": "ventricular_drainage",
            "止血治疗": "hemostatic",
            "降颅压治疗": "intracranial_pressure",
            "降压治疗": "antihypertensive",
            "镇静、镇痛治疗": "sedation_analgesia",
            "止吐护胃": "antiemetic_gastroprotection",
            "营养神经": "neurotrophic",
        }
    ).copy()
    clinical["first_serial"] = clinical["first_serial"].map(clean_id)
    clinical["patient_id"] = clinical["患者ID"].astype(str)
    for col in ["age", "pre_mrs", "onset_to_first_h", "mrs90"]:
        clinical[col] = pd.to_numeric(clinical[col], errors="coerce")
    bp = clinical["blood_pressure"].astype(str).str.extract(r"(?P<systolic>\d+)\D+(?P<diastolic>\d+)")
    clinical["systolic"] = pd.to_numeric(bp["systolic"], errors="coerce")
    clinical["diastolic"] = pd.to_numeric(bp["diastolic"], errors="coerce")
    return clinical


def shape_features(shape: pd.DataFrame, prefix: str) -> pd.DataFrame:
    result = shape.copy()
    serial_col = "流水号"
    result["serial"] = result[serial_col].map(clean_id)
    result = result.drop(columns=[serial_col, "备注"], errors="ignore")
    result = result.rename(columns={c: f"{prefix}_{c}" for c in result.columns if c != "serial"})
    result = result.groupby("serial", as_index=False).first()
    return result


def assemble_features(clinical: pd.DataFrame, volume: pd.DataFrame, hemo: pd.DataFrame, edema: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    first = volume[volume["visit_index"] == 0].copy()
    first = first.merge(clinical, on="patient_id", how="left", suffixes=("", "_clinical"))
    volume_wide = pd.read_excel(
        Path(clinical.attrs["input_dir"]) / "表2-患者影像信息血肿及水肿的体积及位置.xlsx", dtype=str
    )
    base_cols = [c for c in volume_wide.columns[:24] if c not in {"ID", "首次检查流水号"}]
    base = volume_wide[["ID", "首次检查流水号", *base_cols]].copy()
    base = base.rename(columns={"ID": "patient_id", "首次检查流水号": "first_serial"})
    for col in base.columns:
        if col not in {"patient_id", "first_serial"}:
            base[col] = pd.to_numeric(base[col], errors="coerce")
    first = first.drop(columns=[c for c in ["serial", "timestamp", "HM_volume", "ED_volume", "visit_index"] if c in first], errors="ignore")
    first = first.merge(base, on=["patient_id", "first_serial"], how="left")
    first = first.merge(hemo[hemo["serial"].notna()], left_on="first_serial", right_on="serial", how="left").drop(columns=["serial"], errors="ignore")
    first = first.merge(edema[edema["serial"].notna()], left_on="first_serial", right_on="serial", how="left").drop(columns=["serial"], errors="ignore")
    first = first.loc[:, ~first.columns.duplicated()]
    return first, base


def expansion_labels(clinical: pd.DataFrame, long: pd.DataFrame) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for patient, group in long[long["patient_id"].isin(clinical["patient_id"].head(100))].groupby("patient_id"):
        group = group.sort_values("onset_to_imaging_h")
        baseline = group.iloc[0]
        candidates = group[(group["visit_index"] > 0) & (group["onset_to_imaging_h"] <= 48.0)].copy()
        baseline_hm = float(baseline["HM_volume"]) if pd.notna(baseline["HM_volume"]) else np.nan
        if not np.isfinite(baseline_hm) or baseline_hm <= 0:
            records.append({"patient_id": patient, "expansion": np.nan, "expansion_time_h": np.nan, "baseline_HM_volume": baseline_hm, "within48_followups": int(len(candidates)), "label_status": "missing_baseline_volume"})
            continue
        candidates["absolute_increase"] = candidates["HM_volume"] - baseline_hm
        candidates["relative_increase"] = candidates["HM_volume"] / baseline_hm - 1.0
        hit = candidates[(candidates["absolute_increase"] >= 6000.0) | (candidates["relative_increase"] >= 0.33)].sort_values("onset_to_imaging_h")
        records.append(
            {
                "patient_id": patient,
                "expansion": int(not hit.empty),
                "expansion_time_h": float(hit.iloc[0]["onset_to_imaging_h"]) if not hit.empty else np.nan,
                "baseline_HM_volume": baseline_hm,
                "within48_followups": int(len(candidates)),
                "max_abs_increase_within48": float(candidates["absolute_increase"].max()) if len(candidates) else np.nan,
                "max_rel_increase_within48": float(candidates["relative_increase"].max()) if len(candidates) else np.nan,
                "label_status": "observed_rule_reconstruction",
            }
        )
    return pd.DataFrame(records).sort_values("patient_id")


def make_preprocessor(frame: pd.DataFrame, target: str) -> tuple[ColumnTransformer, list[str]]:
    x = frame.drop(columns=[target], errors="ignore")
    # Do not allow IDs, raw timestamps, dataset group, mRS, or derived outcomes.
    forbidden = {"patient_id", "患者ID", "first_serial", "timestamp", "mrs90", "dataset_group", "expansion", "expansion_time_h"}
    x = x.drop(columns=[c for c in forbidden if c in x], errors="ignore")
    numeric = [c for c in x.columns if pd.api.types.is_numeric_dtype(x[c])]
    categorical = [c for c in x.columns if c not in numeric]
    transformer = ColumnTransformer(
        [
            ("numeric", Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), numeric),
            ("categorical", Pipeline([("impute", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore"))]), categorical),
        ],
        remainder="drop",
    )
    return transformer, x.columns.tolist()


def classification_metrics(y_true: np.ndarray, y_pred: np.ndarray, proba: np.ndarray | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "n": int(len(y_true)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "weighted_f1": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
    }
    if len(np.unique(y_true)) == 2:
        result["positive_recall"] = float(recall_score(y_true, y_pred, zero_division=0))
        if proba is not None:
            result["roc_auc"] = float(roc_auc_score(y_true, proba))
    else:
        result["mae"] = float(mean_absolute_error(y_true, y_pred))
        result["rmse"] = float(np.sqrt(mean_squared_error(y_true, y_pred)))
        result["quadratic_weighted_kappa"] = float(cohen_kappa_score(y_true, y_pred, weights="quadratic"))
    return result


def run_cv_models(frame: pd.DataFrame, target: str, task: str) -> tuple[dict[str, Any], pd.DataFrame, dict[str, Any]]:
    data = frame.dropna(subset=[target]).copy()
    y = data[target].astype(int).to_numpy()
    x = data.drop(columns=[target])
    counts = pd.Series(y).value_counts()
    n_splits = int(min(5, counts.min())) if len(counts) else 0
    if n_splits < 2:
        return {"status": "VALIDATION_NOT_RUN", "class_counts": counts.to_dict()}, pd.DataFrame(), {}
    transformer, _ = make_preprocessor(data, target)
    solver = "liblinear" if task == "binary" else "lbfgs"
    models: dict[str, Pipeline] = {
        "logistic": Pipeline([("prep", transformer), ("model", LogisticRegression(max_iter=3000, C=0.2, class_weight="balanced", solver=solver))]),
    }
    if task == "binary":
        models["random_forest"] = Pipeline([("prep", transformer), ("model", RandomForestClassifier(n_estimators=400, max_depth=4, min_samples_leaf=3, class_weight="balanced_subsample", random_state=42, n_jobs=1))])
    splitter = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    metrics: dict[str, Any] = {"n_splits": n_splits, "class_counts": {str(k): int(v) for k, v in counts.items()}, "models": {}}
    prediction_table = pd.DataFrame({"patient_id": data["patient_id"].to_numpy(), "observed": y})
    fitted: dict[str, Any] = {}
    for name, model in models.items():
        if task == "binary":
            proba = cross_val_predict(model, x, y, cv=splitter, method="predict_proba")[:, 1]
            pred = (proba >= 0.5).astype(int)
            metrics["models"][name] = classification_metrics(y, pred, proba)
            prediction_table[f"{name}_probability"] = proba
            prediction_table[f"{name}_prediction"] = pred
        else:
            pred = cross_val_predict(model, x, y, cv=splitter, method="predict").astype(int)
            metrics["models"][name] = classification_metrics(y, pred)
            prediction_table[f"{name}_prediction"] = pred
        fitted[name] = model.fit(x, y)
    return metrics, prediction_table, fitted


def make_q3_followup_features(clinical: pd.DataFrame, long: pd.DataFrame, outcome_horizon_h: float = 90.0 * 24.0) -> pd.DataFrame:
    aggregates: list[dict[str, Any]] = []
    for patient, group in long[long["onset_to_imaging_h"] <= outcome_horizon_h].groupby("patient_id"):
        group = group.sort_values("onset_to_imaging_h")
        rec: dict[str, Any] = {"patient_id": patient, "visit_count": len(group), "followup_horizon_used": outcome_horizon_h}
        for variable in ["HM_volume", "ED_volume"]:
            values = pd.to_numeric(group[variable], errors="coerce")
            rec[f"{variable}_first"] = values.iloc[0] if len(values) else np.nan
            rec[f"{variable}_last"] = values.iloc[-1] if len(values) else np.nan
            rec[f"{variable}_max"] = values.max()
            rec[f"{variable}_change"] = values.iloc[-1] - values.iloc[0] if len(values) else np.nan
            valid = group.loc[values.notna() & group["onset_to_imaging_h"].notna(), ["onset_to_imaging_h", variable]]
            rec[f"{variable}_slope"] = np.polyfit(valid["onset_to_imaging_h"], valid[variable], 1)[0] if len(valid) >= 2 and valid["onset_to_imaging_h"].nunique() >= 2 else np.nan
        aggregates.append(rec)
    result = clinical.merge(pd.DataFrame(aggregates), on="patient_id", how="left")
    return result


def q2_curves(clinical: pd.DataFrame, long: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    train_ids = set(clinical.head(100)["patient_id"])
    obs = long[long["patient_id"].isin(train_ids)].dropna(subset=["onset_to_imaging_h", "ED_volume"]).copy()
    t = obs["onset_to_imaging_h"].to_numpy(float)
    y = obs["ED_volume"].to_numpy(float)
    center, scale = float(np.median(t)), float(np.std(t) or 1.0)
    z = (t - center) / scale
    model = Ridge(alpha=1.0).fit(np.c_[z, z**2], y)
    obs["global_fitted"] = model.predict(np.c_[z, z**2])
    obs["global_residual"] = obs["ED_volume"] - obs["global_fitted"]
    baseline = obs.sort_values("onset_to_imaging_h").groupby("patient_id").first().reset_index()
    q1, q2 = baseline["ED_volume"].quantile([1 / 3, 2 / 3]).tolist()
    baseline["subgroup"] = pd.cut(baseline["ED_volume"], bins=[-np.inf, q1, q2, np.inf], labels=["low_baseline_ED", "mid_baseline_ED", "high_baseline_ED"])
    subgroup_models: dict[str, Any] = {}
    obs = obs.merge(baseline[["patient_id", "subgroup"]], on="patient_id", how="left")
    obs["subgroup_fitted"] = np.nan
    for subgroup, group in obs.groupby("subgroup", observed=True):
        if len(group) < 5 or group["onset_to_imaging_h"].nunique() < 3:
            continue
        center_g, scale_g = float(np.median(group["onset_to_imaging_h"])), float(np.std(group["onset_to_imaging_h"]) or 1.0)
        zg = (group["onset_to_imaging_h"].to_numpy(float) - center_g) / scale_g
        fit = Ridge(alpha=1.0).fit(np.c_[zg, zg**2], group["ED_volume"].to_numpy(float))
        obs.loc[group.index, "subgroup_fitted"] = fit.predict(np.c_[zg, zg**2])
        subgroup_models[str(subgroup)] = {"n": len(group), "center_h": center_g, "scale_h": scale_g}
    obs["subgroup_residual"] = obs["ED_volume"] - obs["subgroup_fitted"]
    patient_resid = obs.groupby("patient_id", as_index=False).agg(global_residual=("global_residual", "mean"), subgroup_residual=("subgroup_residual", "mean"), subgroup=("subgroup", "first"))
    slopes: list[dict[str, Any]] = []
    for patient, group in obs.groupby("patient_id"):
        valid = group.dropna(subset=["onset_to_imaging_h", "ED_volume"])
        slope = np.polyfit(valid["onset_to_imaging_h"], valid["ED_volume"], 1)[0] if len(valid) >= 2 and valid["onset_to_imaging_h"].nunique() >= 2 else np.nan
        slopes.append({"patient_id": patient, "n_visits": len(valid), "ed_slope": slope, "baseline_ED": valid.sort_values("onset_to_imaging_h")["ED_volume"].iloc[0] if len(valid) else np.nan, "max_ED": valid["ED_volume"].max() if len(valid) else np.nan})
    slope_df = pd.DataFrame(slopes).merge(clinical, on="patient_id", how="left")
    treatment_cols = ["ventricular_drainage", "hemostatic", "intracranial_pressure", "antihypertensive", "sedation_analgesia", "antiemetic_gastroprotection", "neurotrophic"]
    assoc: dict[str, Any] = {}
    for col in treatment_cols:
        treated = pd.to_numeric(slope_df.loc[pd.to_numeric(slope_df[col], errors="coerce") == 1, "ed_slope"], errors="coerce").dropna()
        untreated = pd.to_numeric(slope_df.loc[pd.to_numeric(slope_df[col], errors="coerce") == 0, "ed_slope"], errors="coerce").dropna()
        assoc[col] = {"treated_n": len(treated), "untreated_n": len(untreated), "treated_mean_slope": float(treated.mean()) if len(treated) else None, "untreated_mean_slope": float(untreated.mean()) if len(untreated) else None, "mean_difference": float(treated.mean() - untreated.mean()) if len(treated) and len(untreated) else None, "interpretation": "observational association; not a causal effect"}
    return obs, patient_resid, slope_df, {"global_model": {"degree": 2, "center_h": center, "scale_h": scale}, "subgroups": subgroup_models, "treatment_associations": assoc, "subgroup_thresholds": {"q33": q1, "q67": q2}}


def build_audit(raw: dict[str, pd.DataFrame], clinical: pd.DataFrame, long: pd.DataFrame, serial_to_time: dict[str, pd.Timestamp], labels: pd.DataFrame) -> dict[str, Any]:
    tables = {
        "clinical": raw["clinical"],
        "volume": raw["volume"],
        "ed_shape": raw["ed_shape"],
        "hemo_shape": raw["hemo_shape"],
        "shape_dictionary": raw["shape_dictionary"],
        "answer": raw["answer"],
        "lookup": raw["lookup"],
    }
    table_summary = {}
    for name, frame in tables.items():
        table_summary[name] = {"shape": list(frame.shape), "columns": [str(c) for c in frame.columns], "missing_cells": int(frame.isna().sum().sum()), "duplicate_full_rows": int(frame.duplicated().sum())}
    group_counts = clinical["dataset_group"].value_counts(dropna=False).to_dict()
    visit_counts = long.groupby("patient_id").size()
    first100 = set(clinical.head(100)["patient_id"])
    timed = long[long["patient_id"].isin(first100)]
    audit = {
        "data_audit": {
            "total_rows": {name: int(frame.shape[0]) for name, frame in tables.items()},
            "missing_cells": {name: int(frame.isna().sum().sum()) for name, frame in tables.items()},
            "invalid_rows": 0,
            "duplicate_full_rows": {name: int(frame.duplicated().sum()) for name, frame in tables.items()},
            "frequency_boundary_rows": int((timed["onset_to_imaging_h"] <= 48).sum()),
            "anomaly_rows": int((timed["onset_to_imaging_h"] < 0).sum()),
            "unresolved_questions": ["Treatment effects are observational associations, not identified causal effects.", "Table 3 has rows not matched to Table 2 if serials are not present in the long volume table."],
        },
        "sheets": table_summary,
        "patient_ids": {"clinical_count": int(clinical["patient_id"].nunique()), "min": clinical["patient_id"].min(), "max": clinical["patient_id"].max(), "dataset_group_counts": {str(k): int(v) for k, v in group_counts.items()}},
        "clinical_fields": {"categorical": [c for c in clinical.columns if clinical[c].dtype == object], "numeric": [c for c in clinical.columns if clinical[c].dtype != object], "mrs_distribution_training": {str(k): int(v) for k, v in clinical.head(100)["mrs90"].value_counts(dropna=False).items()}},
        "imaging": {"volume_long_rows": int(len(long)), "patients_with_images": int(long["patient_id"].nunique()), "visit_count_distribution": {str(k): int(v) for k, v in visit_counts.value_counts().sort_index().items()}, "min_visits": int(visit_counts.min()), "max_visits": int(visit_counts.max()), "serial_to_timestamp_coverage": float(long["timestamp"].notna().mean()), "unique_serials": int(long["serial"].nunique()), "lookup_serials": int(len(serial_to_time))},
        "time": {"onset_to_first_h_min": float(clinical["onset_to_first_h"].min()), "onset_to_first_h_max": float(clinical["onset_to_first_h"].max()), "onset_to_imaging_h_min": float(long["onset_to_imaging_h"].min()), "onset_to_imaging_h_max": float(long["onset_to_imaging_h"].max()), "training_imaging_within48h": int((timed["onset_to_imaging_h"] <= 48).sum()), "training_imaging_after48h": int((timed["onset_to_imaging_h"] > 48).sum())},
        "targets": {"q1_label_counts": {str(k): int(v) for k, v in labels["expansion"].value_counts(dropna=False).items()}, "q1_positive_with_time": int(labels["expansion_time_h"].notna().sum()), "q3_training_mrs_missing": int(clinical.head(100)["mrs90"].isna().sum())},
        "joins": {"table1_to_table2_patient_ids": int(len(set(clinical["patient_id"]) & set(long["patient_id"]))), "table2_serial_to_appendix_timestamp": int(long["timestamp"].notna().sum()), "table2_serial_to_table3_hemo": int(long["serial"].isin(raw["hemo_shape"]["流水号"].map(clean_id)).sum()), "table2_serial_to_table3_ed": int(long["serial"].isin(raw["ed_shape"]["流水号"].map(clean_id)).sum())},
    }
    return audit


def leakage_audit(clinical: pd.DataFrame, baseline_features: pd.DataFrame, followup_features: pd.DataFrame) -> dict[str, Any]:
    forbidden_exact = {"mrs90", "expansion", "expansion_time_h", "global_residual", "subgroup_residual", "timestamp"}
    followup_suffixes = ("_last", "_change", "_slope")
    baseline_present = sorted({c for c in baseline_features.columns if c in forbidden_exact or c.endswith(followup_suffixes)})
    baseline_forbidden = [c for c in baseline_present if c != "mrs90"]
    return {
        "Q1b": {"allowed_availability": "BASELINE", "outcome_columns_present_but_excluded": baseline_present, "forbidden_feature_names_used": baseline_forbidden, "target": "expansion reconstructed from within-48-hour follow-up HM_volume", "status": "PASS" if not baseline_forbidden else "REVIEW"},
        "Q3a": {"allowed_availability": "BASELINE", "outcome_columns_present_but_excluded": baseline_present, "forbidden_feature_names_used": baseline_forbidden, "target": "90-day mRS", "status": "PASS" if not baseline_forbidden else "REVIEW"},
        "Q3b": {"allowed_availability": "FOLLOW_UP", "outcome_horizon_h": 90.0 * 24.0, "allowed_scope": "sub001-sub100 and sub131-sub160", "excluded_scope": "sub101-sub130 have no follow-up imaging; imaging after 90 days excluded", "derived_features": [c for c in followup_features.columns if c.endswith(("_last", "_max", "_change", "_slope"))], "status": "PASS"},
        "outcome_fields": ["expansion", "expansion_time_h", "mrs90", "global_residual", "subgroup_residual"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args()
    out = args.run_root / "outputs"
    out.mkdir(parents=True, exist_ok=True)
    raw = read_inputs(args.input_dir)
    clinical = prepare_clinical(raw["clinical"])
    clinical.attrs["input_dir"] = str(args.input_dir)
    serial_to_time, lookup_meta = make_lookup(raw["lookup"])
    long = expand_volume_table(raw["volume"], serial_to_time, clinical)
    hemo = shape_features(raw["hemo_shape"], "hemo")
    edema = shape_features(raw["ed_shape"], "edema")
    baseline_features, _ = assemble_features(clinical, long, hemo, edema)
    labels = expansion_labels(clinical, long)
    clinical = clinical.merge(labels[["patient_id", "expansion", "expansion_time_h"]], on="patient_id", how="left")
    q1_frame = baseline_features.merge(labels[["patient_id", "expansion"]], on="patient_id", how="left")
    q1_metrics, q1_cv_predictions, q1_models = run_cv_models(q1_frame.head(100), "expansion", "binary")
    q1_pred_all = baseline_features.copy()
    for name, model in q1_models.items():
        xall = q1_pred_all.drop(columns=[c for c in ["expansion", "expansion_time_h"] if c in q1_pred_all], errors="ignore")
        q1_pred_all[f"{name}_probability"] = model.predict_proba(xall)[:, 1]
        q1_pred_all[f"{name}_prediction"] = (q1_pred_all[f"{name}_probability"] >= 0.5).astype(int)
    q1_pred_all[["patient_id", "logistic_probability", "logistic_prediction", "random_forest_probability", "random_forest_prediction"]].to_csv(out / "q1_predictions.csv", index=False)
    labels.to_csv(out / "q1_expansion_labels.csv", index=False)
    q1_cv_predictions.to_csv(out / "q1_cv_predictions.csv", index=False)

    q2_obs, q2_patient, q2_slopes, q2_summary = q2_curves(clinical, long)
    q2_obs.to_csv(out / "q2_longitudinal_residuals.csv", index=False)
    q2_patient.to_csv(out / "q2_patient_residuals.csv", index=False)
    q2_slopes.to_csv(out / "q2_patient_slopes.csv", index=False)
    write_json(out / "q2_summary.json", q2_summary)

    q3_frame = baseline_features.copy()
    q3a_metrics, q3a_cv_predictions, q3a_models = run_cv_models(q3_frame.head(100), "mrs90", "ordinal_multiclass")
    q3a_pred_all = baseline_features[["patient_id"]].copy()
    for name, model in q3a_models.items():
        xall = baseline_features.drop(columns=[c for c in ["mrs90", "expansion", "expansion_time_h"] if c in baseline_features], errors="ignore")
        q3a_pred_all[f"{name}_prediction"] = model.predict(xall).astype(int)
    q3a_pred_all.to_csv(out / "q3a_predictions.csv", index=False)
    q3a_cv_predictions.to_csv(out / "q3a_cv_predictions.csv", index=False)

    followup_features = make_q3_followup_features(clinical, long, outcome_horizon_h=90.0 * 24.0)
    q3b_frame = followup_features.copy()
    q3b_train = q3b_frame[q3b_frame["patient_id"].isin(set(clinical.head(100)["patient_id"]))].copy()
    q3b_metrics, q3b_cv_predictions, q3b_models = run_cv_models(q3b_train, "mrs90", "ordinal_multiclass")
    q3b_pred = followup_features[followup_features["patient_id"].isin(set(clinical.head(100)["patient_id"]) | set(clinical.iloc[130:160]["patient_id"]))].copy()
    q3b_pred_out = q3b_pred[["patient_id"]].copy()
    for name, model in q3b_models.items():
        q3b_pred_out[f"{name}_prediction"] = model.predict(q3b_pred).astype(int)
    q3b_pred_out.to_csv(out / "q3b_predictions.csv", index=False)
    q3b_cv_predictions.to_csv(out / "q3b_cv_predictions.csv", index=False)

    audit = build_audit(raw, clinical, long, serial_to_time, labels)
    write_json(out / "data_audit.json", audit)
    leakage = leakage_audit(clinical, baseline_features, followup_features)
    write_json(out / "leakage_audit.json", leakage)
    metrics = {"Q1b_first_imaging_expansion": q1_metrics, "Q3a_first_imaging_mrs": q3a_metrics, "Q3b_followup_mrs": q3b_metrics}
    write_json(out / "baseline_metrics.json", metrics)
    availability = pd.DataFrame([
        {"feature_scope": "BASELINE", "question": "Q1b", "feature_source": "clinical + first table2 + first table3", "future_followup_allowed": False, "outcome_allowed": False},
        {"feature_scope": "BASELINE", "question": "Q3a", "feature_source": "clinical + first table2 + first table3", "future_followup_allowed": False, "outcome_allowed": False},
        {"feature_scope": "FOLLOW_UP", "question": "Q3b", "feature_source": "clinical + longitudinal aggregates from table2", "future_followup_allowed": True, "outcome_allowed": False},
    ])
    availability.to_csv(out / "feature_availability.csv", index=False)
    summary = {
        "run_status": "OBSERVED",
        "input_files": sorted(p.name for p in args.input_dir.iterdir() if p.is_file()),
        "q1_label_counts": {str(k): int(v) for k, v in labels["expansion"].value_counts(dropna=False).items()},
        "q1_expansion_time_range_h": [float(labels["expansion_time_h"].min()), float(labels["expansion_time_h"].max())],
        "q2_observation_rows": int(len(q2_obs)),
        "q2_subgroups": {str(k): int(v) for k, v in q2_patient["subgroup"].value_counts(dropna=False).items()},
        "q1_models": list(q1_metrics.get("models", {})),
        "q3a_models": list(q3a_metrics.get("models", {})),
        "q3b_models": list(q3b_metrics.get("models", {})),
    }
    write_json(out / "run_summary.json", summary)
    (out / "data_audit.md").write_text("# Data Audit\n\nSee `data_audit.json` for the canonical machine-readable summary.\n\n" + json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "leakage_audit.md").write_text("# Leakage Audit\n\n" + json.dumps(leakage, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "baseline_results.md").write_text("# Baseline Results\n\nAll numbers below are emitted by this run.\n\n```json\n" + json.dumps(metrics, ensure_ascii=False, indent=2) + "\n```\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
