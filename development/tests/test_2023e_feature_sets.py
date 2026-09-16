"""Independent Q3 feature-set experiment; frozen helpers/inputs are read only.

CLI: python -m development.tests.test_2023e_feature_sets --output <new-run-directory>
Tests write exclusively into pytest tmp_path. No model or threshold tuning.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import warnings

import numpy as np
import pandas as pd
import sklearn
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.exceptions import ConvergenceWarning
import yaml

from development.tests.test_2023e_ordinal_q3 import _load_frozen_baseline_module, RAW, BASELINE_SCRIPT, LEVELS, PROJECT
from skill.scripts.feature_sets import (feature_set_errors, audit_feature_comparison, paired_metric_summary,
    apply_feature_set_gate, ORDINAL_METRICS, IMBALANCE_METRICS, METRIC_DIRECTIONS)
from skill.scripts.group_validation import group_structure_contract, validate_group_cv_splits
from skill.scripts.temporal_availability import filter_before_aggregation, assert_temporal_aggregation_input
from skill.scripts.ordinal import ordinal_metrics
from skill.scripts.metrics import (evaluate_binary_threshold, majority_class_baseline, feature_sample_size_check,
    imbalanced_model_selection_check)
from skill.scripts.runtime_provenance import (apply_group_gate, apply_temporal_gate, sha256,
    validate_experiment_record, validate_workspace_manifest)


THERAPIES = ["ventricular_drainage", "hemostatic", "intracranial_pressure", "antihypertensive",
    "sedation_analgesia", "antiemetic_gastroprotection", "neurotrophic"]
FORBIDDEN = ["patient_id", "患者ID", "first_serial", "mrs90", "dataset_group"]
Q3_PLAN = {"B0": ["initial", "volume", "location", "shape", "intensity"],
    "B0_F1": ["initial", "volume", "location", "shape", "intensity", "followup_volume"],
    "FULL": ["initial", "volume", "location", "shape", "intensity", "followup_volume", "followup_time"],
    "DROP_F1": ["initial", "volume", "location", "shape", "intensity", "followup_time"],
    "THIN": ["initial", "volume", "followup_volume", "followup_time"]}
Q3_PARENTS = {"B0": None, "B0_F1": "B0", "FULL": "B0_F1", "DROP_F1": "FULL", "THIN": "FULL"}


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")


def group(name, columns, *, source, rationale, temporal_role="BASELINE", builder=None):
    return dict(name=name, description=rationale, source=source,
        columns_or_builder={"columns": columns, **(builder or {})}, availability="VERIFIED",
        temporal_role=temporal_role, entity_level="ENTITY", dimension=len(columns),
        domain_rationale=rationale, required_or_optional="OPTIONAL")


def assemble():
    module = _load_frozen_baseline_module()
    raw = module.read_inputs(RAW)
    clinical = module.prepare_clinical(raw["clinical"])
    clinical.attrs["input_dir"] = str(RAW)
    serial_time, _ = module.make_lookup(raw["lookup"])
    longitudinal = module.expand_volume_table(raw["volume"], serial_time, clinical)
    baseline, _ = module.assemble_features(clinical, longitudinal,
        module.shape_features(raw["hemo_shape"], "hemo"), module.shape_features(raw["ed_shape"], "edema"))
    ids = clinical.patient_id.head(100).tolist()
    baseline = baseline.set_index("patient_id").loc[ids].reset_index()
    assert len(baseline) == baseline.patient_id.nunique() == 100
    assert baseline.mrs90.notna().all()
    assert raw["hemo_shape"]["流水号"].is_unique and raw["ed_shape"]["流水号"].is_unique
    # Only source rows belonging to the eligible labelled entities are considered.
    all_future = longitudinal[longitudinal.onset_to_imaging_h > 2160.]
    all_source_audit = dict(n_rows=len(longitudinal), n_entities=int(longitudinal.patient_id.nunique()),
        post_horizon_rows=len(all_future), affected_entities=int(all_future.patient_id.nunique()))
    longitudinal = longitudinal[longitudinal.patient_id.isin(ids)].copy()
    assert longitudinal.onset_to_imaging_h.notna().all() and (longitudinal.onset_to_imaging_h >= 0).all()
    legal, temporal = filter_before_aggregation(longitudinal, time_column="onset_to_imaging_h",
        cutoff=2160., prediction_as_of_time=2160., target_time=2160., entity_key="patient_id", target="mrs90", task="Q3 controlled information comparison")
    assert_temporal_aggregation_input(legal, temporal)
    rows = []
    for entity, g in legal.groupby("patient_id", sort=True):
        g = g.sort_values(["onset_to_imaging_h", "visit_index"])
        t = g.onset_to_imaging_h.to_numpy(float)
        r = dict(patient_id=entity, last_observation_h=float(t[-1]), observation_span_h=float(t[-1]-t[0]), visit_count=len(g))
        for variable in ("HM_volume", "ED_volume"):
            values = g[variable].to_numpy(float)
            r.update({f"{variable}_last": float(values[-1]), f"{variable}_max": float(np.nanmax(values)),
                f"{variable}_change": float(values[-1]-values[0])})
            finite = np.isfinite(values) & np.isfinite(t)
            r[f"{variable}_slope"] = float(np.polyfit(t[finite], values[finite], 1)[0]) if finite.sum() >= 2 and len(set(t[finite])) >= 2 else np.nan
        rows.append(r)
    frame = baseline.merge(pd.DataFrame(rows), on="patient_id", how="left", validate="one_to_one")
    volumes = ["HM_volume", "ED_volume"]
    location = [c for c in baseline if c.endswith("_Ratio") and c.startswith(("HM_", "ED_"))]
    shape = [c for c in baseline if "_original_shape_" in c]
    intensity = [c for c in baseline if "_NCCT_original_firstorder_" in c]
    initial = [c for c in baseline if c not in FORBIDDEN + THERAPIES + volumes + location + shape + intensity]
    assert len(location) == 20 and len(shape) == 28 and len(intensity) == 34
    # Preserve even redundant legal baseline encodings to avoid hidden composition changes.
    assert "blood_pressure" in initial and "onset_to_imaging_h" in initial
    f1 = [f"{v}_{s}" for v in volumes for s in ("last", "max", "change")]
    f2 = [f"{v}_slope" for v in volumes] + ["last_observation_h", "observation_span_h", "visit_count"]
    groups = [
        group("initial", initial, source="table1 + first examination timing", rationale="initial personal, history, pressure and timing fields"),
        group("volume", volumes, source="table2 first examination", rationale="initial lesion sizes"),
        group("location", location, source="table2 first examination", rationale="anatomical distribution ratios"),
        group("shape", shape, source="table3 initial serial join", rationale="initial geometric descriptors"),
        group("intensity", intensity, source="table3 initial serial join", rationale="initial intensity distribution descriptors"),
        group("followup_volume", f1, source="table2 legal per-entity rows", rationale="additional volume extent and endpoint summaries", temporal_role="FOLLOWUP_TO_CUTOFF",
            builder=dict(derived=True, inputs=volumes + ["patient_id", "onset_to_imaging_h"], units="original volume units (10^-3 mL)",
                formula="filter 0<=time<=2160h, within entity sort by time; latest, max, latest-first (including first observation)")),
        group("followup_time", f2, source="table2 + lookup times legal per-entity rows", rationale="rates and observation timing; care-process information is not biological causality", temporal_role="FOLLOWUP_TO_CUTOFF",
            builder=dict(derived=True, inputs=volumes + ["patient_id", "onset_to_imaging_h"], units="volume unit/hour; hours; count",
                formula="same filtered rows; OLS degree-one slope per volume; last time, last-first time, number of visits; <2 unique times -> missing slope")),
    ]
    assert set(initial + volumes + location + shape + intensity) == set(baseline.columns) - set(FORBIDDEN + THERAPIES)
    labels = module.expansion_labels(clinical, longitudinal)
    y1 = labels.set_index("patient_id").loc[ids].expansion.astype(int).to_numpy()
    audit = dict(all_source_scope=all_source_audit, n_entities=100, n_rows_before_filter=len(longitudinal), n_rows_after_filter=len(legal),
        post_horizon_records_excluded=temporal["post_horizon_records"], affected_entities=temporal["excluded_entity_count"],
        minimum_time_h=float(legal.onset_to_imaging_h.min()), maximum_time_h=float(legal.onset_to_imaging_h.max()),
        first_time_range_h=[float(baseline.onset_to_first_h.min()), float(baseline.onset_to_first_h.max())],
        mrs_counts={str(k): int(v) for k, v in frame.mrs90.value_counts().sort_index().items()},
        baseline_exclusions={**{c: "identifier, dataset partition or target; not predictor" for c in FORBIDDEN},
            **{c: "EXPOSURE_TIME_UNVERIFIED: first-examination availability cannot be established" for c in THERAPIES}},
        baseline_information_policy="all remaining legal columns retained including raw/split pressure and duplicate first-time encoding",
        timing_limitation="2160h is the established outcome-horizon information envelope, not early prospective prediction; actual outcome-assessment timestamp is unavailable",
        aggregation_policy="filter before any per-entity summary; no learned transformation or target-guided grouping outside CV",
        missing_cells_by_group={g["name"]: int(frame[g["columns_or_builder"]["columns"]].isna().sum().sum()) for g in groups},
        q1_label_limit="historical expansion definition retained; 4 without within-window follow-up coded 0, no Q1 label revision")
    return module, frame, y1, groups, temporal, audit


class FitRowRecorder(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        self.fit_ids_ = X.index.tolist()
        return self

    def transform(self, X):
        return X


def build_records(frame, groups, y, temporal, *, task, run_id, created_at):
    is_q3 = task == "Q3"
    plan = Q3_PLAN if is_q3 else {"C": ["initial"], "C_VL": ["initial", "volume", "location"], "C_VL_SI": Q3_PLAN["B0"]}
    parents = Q3_PARENTS if is_q3 else {"C": None, "C_VL": "C", "C_VL_SI": "C_VL"}
    baseline_groups = plan["B0" if is_q3 else "C"]
    metrics = sorted(ORDINAL_METRICS) if is_q3 else sorted(IMBALANCE_METRICS | {"Accuracy", "Brier Score"})
    primary = "MAE" if is_q3 else "PR-AUC"
    n_splits = 4 if is_q3 else 5
    assert np.bincount(y).min() >= n_splits
    splits = list(RepeatedStratifiedKFold(n_splits=n_splits, n_repeats=2, random_state=42).split(frame, y))
    ids = frame.patient_id.tolist()
    folds = [dict(fold_id=f"r{i//n_splits+1}-f{i%n_splits+1}", train_ids=[ids[j] for j in t], validation_ids=[ids[j] for j in v]) for i, (t, v) in enumerate(splits)]
    contract = dict(task=task, prediction_setting="NEW_ENTITY", unit_of_analysis="ENTITY", target="mrs90" if is_q3 else "expansion",
        feature_groups=groups, baseline_feature_groups=baseline_groups,
        candidate_incremental_groups=[g["name"] for g in groups if g["name"] not in baseline_groups and (is_q3 or g["temporal_role"] == "BASELINE")],
        required_groups=["initial"], optional_groups=[g["name"] for g in groups if g["name"] != "initial"], excluded_groups=[], exclusion_reason={},
        temporal_scope=dict(status="PASS", horizon_h=2160., interpretation="outcome-horizon envelope; initial-only arm deliberately withholds follow-up") if is_q3 else dict(status="NOT_APPLICABLE", rationale="initial examination only; unknown-timing treatment flags excluded"),
        group_scope=dict(status="PASS", independence_required=True), selection_method="NONE", selection_scope="NONE",
        comparison_protocol=dict(planned_candidates=list(plan), design_source="PROBLEM_STRUCTURE", search_strategy="PLANNED_SMALL", selection_validation="FIXED_CV",
            rationale="retain baseline then add extent and rate/timing summaries; preplanned single-block drops and old-composition-like diagnostic" if is_q3 else "initial state -> volume/location -> geometric/intensity information",
            practical_deltas={m: .05 if m in {"MAE", "RMSE"} else .02 for m in metrics}, minimum_consistency=.75), status="PASS")
    protocol = dict(target=contract["target"], target_definition="90-day mRS ordered levels 0..6" if is_q3 else "within48h >=6000 volume units or >=33% expansion; frozen labels",
        target_values=y.tolist(), temporal_cutoff=2160. if is_q3 else "initial examination only",
        random_seeds=[42], model_family="regularized LogisticRegression",
        hyperparameter_policy=dict(C=.2, solver="lbfgs" if is_q3 else "liblinear", max_iter=3000, class_weight=None if is_q3 else "balanced", random_state=42),
        preprocessing_policy="frozen helper ColumnTransformer: train-only median+scale numeric; most-frequent+onehot categorical; no variable selection",
        metric_definitions={m: dict(definition=m+" from existing metric helper, same labels/threshold across sets", higher_is_better=METRIC_DIRECTIONS[m]) for m in metrics},
        primary_metric=primary, target_type="ordinal" if is_q3 else "binary", imbalanced=not is_q3)
    structure = group_structure_contract(frame[["patient_id"]], entity_key="patient_id", prediction_setting="NEW_ENTITY", validation_unit="ENTITY",
        task=task, target=contract["target"], aggregated_from_repeated=is_q3,
        aggregation_provenance=dict(within_entity_only=True, temporal_gate_status="PASS", learned_preprocessing_scope="NONE") if is_q3 else None)
    split_report = validate_group_cv_splits(splits, ids, group_key="patient_id", split_strategy=f"RepeatedStratifiedKFold({n_splits}x2,42) on one-row-per-entity table", prediction_setting="NEW_ENTITY", validation_unit="ENTITY")
    records = {}
    for name, selected in plan.items():
        cols = [c for g in groups if g["name"] in selected for c in g["columns_or_builder"]["columns"]]
        omitted_groups = set(baseline_groups) - set(selected)
        removals = [dict(column=c, status="REMOVED_FROM_BASELINE", removal_reason="preplanned old-composition-like diagnostic; not pure follow-up increment") for g in groups if g["name"] in omitted_groups for c in g["columns_or_builder"]["columns"]]
        scope = dict(feature_set_id=name, feature_groups=selected, feature_columns=cols, baseline_feature_set="B0" if is_q3 else "C",
            incremental_groups=[g for g in selected if g not in baseline_groups], removed_groups=sorted(omitted_groups), removals=removals,
            selection_method="NONE", selection_scope="NONE", sample_ids=ids, entity_ids=ids,
            fold_ids=folds, model_family=protocol["model_family"], comparison_parent=parents[name], comparison_reason=contract["comparison_protocol"]["rationale"], protocol=protocol)
        planned = dict(feature_set_comparison=True, validation_unit="ENTITY", group_validation=True,
            temporal_prediction=is_q3, aggregation_required=is_q3, feature_set_id=name, **deepcopy(protocol))
        rec = dict(experiment_id=f"{task}-{name}", run_id=run_id, created_at=created_at, problem="2023E targeted feature-set capability test", question=task,
            status="PLANNED", planned_protocol=planned, executed_protocol=deepcopy(planned), protocol_changed=False,
            change_reason="", comparable_to_original_plan=True, input_artifacts=["raw-inputs"], code_artifacts=["targeted-driver", "feature-guards", "runtime-provenance", "metrics", "ordinal", "group", "temporal", "frozen-assembly"],
            output_artifacts=[], random_seed=42, metrics={}, evidence_ids=[], feature_set_contract=deepcopy(contract), feature_set=deepcopy(scope))
        rec = apply_group_gate(rec, structure, split_report)
        if is_q3:
            rec = apply_temporal_gate(rec, temporal)
        assert not validate_experiment_record(rec), validate_experiment_record(rec)
        records[name] = rec
    return records, splits


def run_task(module, frame, y, records, splits, out):
    # Every planned record, including diagnostics, exists before the first fit.
    for name, r in records.items():
        write(out / "planned" / f"{name}.json", r)
    for name, r in records.items():
        s = r["feature_set"]
        X = frame[s["feature_columns"]].copy()
        X.index = frame.patient_id.tolist()
        preprocessor, used = module.make_preprocessor(X, "mrs90")
        assert used == s["feature_columns"]
        params = s["protocol"]["hyperparameter_policy"]
        s["fold_metrics"], s["fit_log"] = [], []
        predictions, dimensions = [], []
        is_q3 = s["protocol"]["target_type"] == "ordinal"
        r["status"] = "RUNNING"
        write(out / "records" / f"{name}.json", r)
        for i, (train, valid) in enumerate(splits):
            fid = s["fold_ids"][i]["fold_id"]
            model = Pipeline([("fit_rows", FitRowRecorder()), ("prep", deepcopy(preprocessor)), ("model", LogisticRegression(**params))])
            with warnings.catch_warnings():
                warnings.simplefilter("error", ConvergenceWarning)
                model.fit(X.iloc[train], y[train])
            pred = model.predict(X.iloc[valid])
            probability = model.predict_proba(X.iloc[valid])
            m = ordinal_metrics(y[valid], pred, ordered_levels=LEVELS) if is_q3 else evaluate_binary_threshold(y[valid], probability[:, 1], threshold=.5, positive_label=1)
            s["fold_metrics"].append(dict(fold_id=fid, metrics={k: float(m[k]) for k in s["protocol"]["metric_definitions"]}))
            fit_ids = model.named_steps["fit_rows"].fit_ids_
            s["fit_log"].append(dict(fold_id=fid, scope="TRAIN_FOLD", operation="entire unfitted preprocessing/model pipeline", fit_ids=fit_ids))
            r["group_scope"]["folds"][i]["preprocessing"] = [dict(operation="entire pipeline", fit_row_ids=train.tolist())]
            dim = int(model.named_steps["prep"].transform(X.iloc[train]).shape[1])
            dimensions.append(dict(fold_id=fid, **feature_sample_size_check(len(train), dim)))
            for pos, row in enumerate(valid):
                predictions.append(dict(fold_id=fid, sample_id=frame.patient_id.iloc[row], truth=int(y[row]), prediction=int(pred[pos]), probabilities=probability[pos].tolist()))
        names = s["protocol"]["metric_definitions"]
        r["metrics"] = {k: dict(mean=float(np.mean([f["metrics"][k] for f in s["fold_metrics"]])),
            std=float(np.std([f["metrics"][k] for f in s["fold_metrics"]], ddof=1)),
            median=float(np.median([f["metrics"][k] for f in s["fold_metrics"]]))) for k in names}
        r.update(status="OBSERVED", updated_by_workflow="run_experiment", output_artifacts=[f"{r['question']}-{name}-predictions", f"{r['question']}-{name}-record"], evidence_ids=[f"EV-{r['experiment_id']}"])
        r["dimension_audit"] = dict(raw_features=len(X.columns), n_entities=len(X), fold_transformed_dimensions=dimensions,
            missing_cells=int(X.isna().sum().sum()))
        r = apply_feature_set_gate(r)
        assert r["status"] == "OBSERVED" and not validate_experiment_record(r), validate_experiment_record(r)
        records[name] = r
        write(out / "predictions" / f"{name}.json", predictions)
        write(out / "records" / f"{name}.json", r)
    return records


def comparisons(records, pairs):
    results = []
    for a, b, contrast in pairs:
        parent, candidate = deepcopy(records[a]), deepcopy(records[b])
        candidate["feature_set"]["comparison_parent"] = a
        gate = audit_feature_comparison(parent, candidate, contrast=contrast)
        assert gate["status"] == "PASS", gate
        p = candidate["feature_set"]["protocol"]
        policy = candidate["feature_set_contract"]["comparison_protocol"]
        deltas = {k: paired_metric_summary(parent["feature_set"]["fold_metrics"], candidate["feature_set"]["fold_metrics"],
            metric=k, higher_is_better=v["higher_is_better"], practical_delta=policy["practical_deltas"][k], minimum_consistency=policy["minimum_consistency"], contrast=contrast) for k, v in p["metric_definitions"].items()}
        results.append(dict(parent=a, candidate=b, contrast=contrast, gate=gate, paired_metrics=deltas,
            primary_metric=p["primary_metric"], conclusion=deltas[p["primary_metric"]]["status"]))
    return results


def execute(output):
    out = Path(output).resolve()
    out.mkdir(parents=True, exist_ok=False)
    created = datetime.now(timezone.utc).isoformat()
    run_id, benchmark_id = out.name, out.parent.name
    sources = [*RAW.glob("*.xlsx"), BASELINE_SCRIPT]
    manifest = dict(run_id=run_id, benchmark_id=benchmark_id, created_at=created, active_run_id=run_id,
        immutable_inputs=[dict(path=str(p), sha256=sha256(p)) for p in sources], writable_root=str(out), allowed_write_root=str(out),
        prior_run_artifacts_visible=False, allowed_read_roots=[str(RAW), str(BASELINE_SCRIPT), str(PROJECT/"skill")],
        mode="TARGETED_CAPABILITY_TEST", historical_helper_reference=str(BASELINE_SCRIPT),
        note="frozen code reused read-only; no historical results used for model selection; not a blind run")
    assert not validate_workspace_manifest(manifest), validate_workspace_manifest(manifest)
    (out / "workspace-manifest.yaml").write_text(yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False), encoding="utf-8")
    module, frame, y1, groups, temporal, audit = assemble()
    write(out / "data-audit.json", audit)
    write(out / "temporal-contract.json", temporal)
    write(out / "feature-groups.json", groups)
    y3 = frame.mrs90.astype(int).to_numpy()
    q3, splits3 = build_records(frame, groups, y3, temporal, task="Q3", run_id=run_id, created_at=created)
    q1, splits1 = build_records(frame, groups[:5], y1, temporal, task="Q1", run_id=run_id, created_at=created)
    q3pairs = [("B0", "B0_F1", "increment"), ("B0_F1", "FULL", "increment"), ("B0", "FULL", "increment"),
        ("FULL", "DROP_F1", "drop"), ("FULL", "B0_F1", "drop"), ("FULL", "THIN", "drop"), ("B0", "THIN", "composition_diagnostic")]
    q1pairs = [("C", "C_VL", "increment"), ("C_VL", "C_VL_SI", "increment")]
    # Freeze plan and all folds before any model training, including uncertainty policy.
    write(out / "comparison-plan.json", dict(Q3=q3pairs, Q1=q1pairs, Q3_policy=q3["B0"]["feature_set_contract"]["comparison_protocol"], Q1_policy=q1["C"]["feature_set_contract"]["comparison_protocol"],
        model_note="existing nominal regularized logistic held fixed; ordinal metrics retained, no claim of new ordinal estimator",
        stop="no additional candidate after seeing results"))
    write(out / "fold-ids.json", dict(Q3=q3["B0"]["feature_set"]["fold_ids"], Q1=q1["C"]["feature_set"]["fold_ids"]))
    for records, pairs in ((q3, q3pairs), (q1, q1pairs)):
        for a, b, contrast in pairs:
            candidate = deepcopy(records[b]); candidate["feature_set"]["comparison_parent"] = a
            assert audit_feature_comparison(records[a], candidate, contrast=contrast)["status"] == "PASS"
    q3 = run_task(module, frame, y3, q3, splits3, out/"Q3")
    q1 = run_task(module, frame, y1, q1, splits1, out/"Q1")
    # Same-fold naive baselines for interpretation, no extra candidate optimization.
    median_baseline = [dict(fold_id=q3["B0"]["feature_set"]["fold_ids"][i]["fold_id"],
        metrics={k: float(v) for k, v in ordinal_metrics(y3[v], np.repeat(int(np.median(y3[t])), len(v)), ordered_levels=LEVELS).items() if k in ORDINAL_METRICS}) for i, (t, v) in enumerate(splits3)]
    majority = majority_class_baseline(y1, positive_label=1)
    summary = dict(audit=audit, Q3={k: v["metrics"] for k,v in q3.items()}, Q1={k: v["metrics"] for k,v in q1.items()},
        Q3_comparisons=comparisons(q3, q3pairs), Q1_comparisons=comparisons(q1, q1pairs),
        Q3_median_baseline=median_baseline, Q1_majority_baseline=majority,
        Q1_selection_checks={k: imbalanced_model_selection_check({m: s["mean"] for m,s in r["metrics"].items()}, majority_baseline=majority) for k,r in q1.items()},
        versions=dict(python=sys.version, numpy=np.__version__, pandas=pd.__version__, sklearn=sklearn.__version__),
        provenance_status="PASS", model_fits=5*8+3*10)
    write(out / "results.json", summary)
    active = dict(active_run_id=run_id, active_evidence_set={f"{task}-{name}": dict(run_id=run_id, experiment_id=r["experiment_id"], artifact=f"{task}/records/{name}.json") for task, records in (("Q3",q3),("Q1",q1)) for name,r in records.items()})
    (out / "active-evidence-set.yaml").write_text(yaml.safe_dump(active, allow_unicode=True), encoding="utf-8")
    code_sources = {"targeted-driver": Path(__file__), "feature-guards": PROJECT/"skill/scripts/feature_sets.py",
        "runtime-provenance": PROJECT/"skill/scripts/runtime_provenance.py", "frozen-assembly": BASELINE_SCRIPT,
        **{key: PROJECT/f"skill/scripts/{name}.py" for key, name in {"metrics": "metrics", "ordinal": "ordinal", "group": "group_validation", "temporal": "temporal_availability"}.items()}}
    aliases = {"workspace-manifest.yaml": "raw-inputs"}
    for task, records in (("Q3", q3), ("Q1", q1)):
        for name in records:
            aliases[f"{task}/records/{name}.json"] = f"{task}-{name}-record"
            aliases[f"{task}/predictions/{name}.json"] = f"{task}-{name}-predictions"
    ledger = [dict(artifact_id=aliases.get(f.relative_to(out).as_posix(), f.relative_to(out).as_posix()), path=str(f), sha256=sha256(f), run_id=run_id) for f in out.rglob("*") if f.is_file()]
    ledger.extend(dict(artifact_id=key, path=str(f), sha256=sha256(f), run_id=run_id) for key, f in code_sources.items())
    ledger.extend(dict(artifact_id="EV-"+r["experiment_id"], type="EXPERIMENT_RESULT", path=str(out/task/"records"/f"{name}.json"),
        sha256=sha256(out/task/"records"/f"{name}.json"), run_id=run_id, experiment_id=r["experiment_id"]) for task, records in (("Q3",q3),("Q1",q1)) for name, r in records.items())
    registered = {e["artifact_id"] for e in ledger}
    for records in (q3, q1):
        for r in records.values():
            assert set(r["code_artifacts"] + r["input_artifacts"] + r["output_artifacts"] + r["evidence_ids"]) <= registered
    write(out / "evidence-ledger.json", ledger)
    return summary


def test_real_q3_preserves_baseline_and_uses_controlled_folds(tmp_path):
    summary = execute(tmp_path / "feature-set-design" / "run-001")
    assert summary["audit"]["n_entities"] == 100
    assert summary["audit"]["n_rows_before_filter"] == 450
    assert summary["audit"]["post_horizon_records_excluded"] == 7
    assert summary["audit"]["affected_entities"] == 6
    assert summary["audit"]["all_source_scope"]["post_horizon_rows"] == 9
    assert summary["audit"]["all_source_scope"]["affected_entities"] == 8
    assert len(summary["Q3"]) == 5 and len(summary["Q1"]) == 3
    assert all(c["gate"]["status"] == "PASS" for c in summary["Q3_comparisons"] + summary["Q1_comparisons"])
    assert all(len(c["paired_metrics"]["MAE"]["raw_deltas"]) == 8 for c in summary["Q3_comparisons"])


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = execute(args.output)
    print(json.dumps({k: result[k] for k in ("Q3", "Q1", "model_fits")}, ensure_ascii=False, indent=2))
