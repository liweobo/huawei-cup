"""Read-only Q2c/Q2d targeted evidence; no Q1/Q3 or causal model search.

python -B development/tests/test_2023e_association_q2.py --output development/artifacts/observational-association/q2-targeted
"""

from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest

PROJECT = Path(__file__).resolve().parents[2]
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from skill.scripts.association_analysis import (
    AssociationAnalysisError, apply_association_gate, audit_exposures,
    build_association_contract, fit_crude_adjusted_association,
    require_association_contract, review_association_claim,
)
from skill.scripts.group_validation import group_structure_contract
from skill.scripts.runtime_provenance import validate_experiment_record
from skill.scripts.temporal_availability import validate_temporal_availability

RAW = PROJECT / "development/benchmarks/problems/2023/E/raw"
READER = PROJECT / "development/benchmarks/runtime/historical_2023_e_hemorrhagic_stroke/run-001/code/clinical_baseline.py"
INPUTS = {"clinical-input": RAW / "表1-患者列表及临床信息.xlsx",
          "volume-input": RAW / "表2-患者影像信息血肿及水肿的体积及位置.xlsx",
          "time-lookup-input": RAW / "附表1-检索表格-流水号vs时间.xlsx"}
TREATMENTS = ["ventricular_drainage", "hemostatic", "intracranial_pressure", "antihypertensive",
              "sedation_analgesia", "antiemetic_gastroprotection", "neurotrophic"]
LABELS = ["脑室引流", "止血治疗", "降颅压治疗", "降压治疗", "镇静、镇痛治疗", "止吐护胃", "营养神经"]
ADJUSTMENT = ["age_decades_from_60", "male", "hypertension"]
TIME = "log_time_from_day7"
RUN_ID = "observational-association-q2-targeted"


def _write(path: Path, value):
    def convert(item):
        if hasattr(item, "item"):
            return item.item()
        if isinstance(item, (np.ndarray, pd.Index)):
            return item.tolist()
        raise TypeError(type(item).__name__)
    path.write_text(json.dumps(value, default=convert, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")


def _sha(path):
    with Path(path).open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def _read_data():
    spec = importlib.util.spec_from_file_location("association_readonly_source", READER)
    assert spec and spec.loader
    source = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(source)
    # Reuse only source parsing, never the old q2_curves() or any Q1/Q3 model.
    raw_clinical = pd.read_excel(INPUTS["clinical-input"], dtype=str)
    clinical = source.prepare_clinical(raw_clinical).head(100).copy()
    assert set(clinical["patient_id"]) == {f"sub{number:03d}" for number in range(1, 101)}
    lookup, _ = source.make_lookup(pd.read_excel(INPUTS["time-lookup-input"], dtype=str))
    observations = source.expand_volume_table(pd.read_excel(INPUTS["volume-input"], dtype=str), lookup, clinical)
    observations = observations[observations["patient_id"].isin(clinical["patient_id"])].copy()
    assert len(clinical) == 100 and len(observations) == 450
    assert observations[["ED_volume", "HM_volume", "onset_to_imaging_h"]].notna().all().all()
    assert (observations["onset_to_imaging_h"] >= 0).all()
    clinical["male"] = clinical["sex"].map({"男": 1, "女": 0})
    clinical["age_decades_from_60"] = (clinical["age"] - 60) / 10
    for name in [*TREATMENTS, "hypertension"]:
        clinical[name] = pd.to_numeric(clinical[name], errors="raise")
        assert set(clinical[name].unique()) <= {0, 1}
    assert clinical["male"].notna().all()
    observations = observations.merge(clinical[["patient_id", "age", "pre_mrs", *ADJUSTMENT, *TREATMENTS]],
                                      on="patient_id", how="left", validate="many_to_one").reset_index(drop=True)
    # The source states volumes in 10^-3 mL. All reported new coefficients use mL.
    observations["ED_ml"] = observations["ED_volume"] / 1000
    observations["HM_ml"] = observations["HM_volume"] / 1000
    observations[TIME] = np.log1p(observations["onset_to_imaging_h"] / 24) - np.log1p(7)
    initial = observations[observations["visit_index"] == 0].set_index("patient_id")
    assert len(initial) == 100 and initial.index.is_unique
    assert initial["onset_to_imaging_h"].sort_index().equals(observations.groupby("patient_id")["onset_to_imaging_h"].min().sort_index())
    for source_name, new_name in [("HM_ml", "initial_HM_ml"), ("ED_ml", "initial_ED_ml"),
                                  ("onset_to_imaging_h", "initial_time_h")]:
        observations[new_name] = observations["patient_id"].map(initial[source_name])
    availability = []
    for row in observations.itertuples():
        gate = validate_temporal_availability([row.initial_time_h, row.onset_to_imaging_h],
                                             cutoff=row.onset_to_imaging_h, target_time=row.onset_to_imaging_h)
        assert gate["status"] == "PASS" and gate["post_horizon_records"] == 0
        availability.append({"row_id": row.Index, "entity_id": row.patient_id,
                             "initial_time_h": row.initial_time_h, "outcome_time_h": row.onset_to_imaging_h,
                             "concurrent_HM_time_h": row.onset_to_imaging_h, "gate_status": gate["status"]})
    # Only after the source-time checks may initial/current measurements enter
    # the descriptive change variables. None is a pre-treatment confounder.
    observations["ED_change_ml"] = observations["ED_ml"] - observations["initial_ED_ml"]
    observations["initial_HM_per_10ml"] = observations["initial_HM_ml"] / 10
    observations["HM_change_per_10ml"] = (observations["HM_ml"] - observations["initial_HM_ml"]) / 10
    return observations, raw_clinical.columns.tolist(), availability


def _contract(data, exposures, outcome, *, joint=False):
    return build_association_contract(
        exposure=exposures, outcome=outcome, assignment_type="OBSERVATIONAL", exposure_time_known=False,
        candidate_confounders=[
            {"name": "age_decades_from_60", "temporal_role": "PRE_EXPOSURE",
             "evidence": "Table 1 age: pre-existing demographic attribute; fixed centering/scaling"},
            {"name": "male", "temporal_role": "PRE_EXPOSURE",
             "evidence": "Table 1 sex: pre-existing recorded demographic attribute"},
            {"name": "hypertension", "temporal_role": "PRE_EXPOSURE",
             "evidence": "Table 1 高血压病史 explicitly describes prior history, not treatment response"},
            {"name": "initial_HM_per_10ml", "temporal_role": "UNKNOWN",
             "evidence": "first imaging time is known; treatment time is not"},
            {"name": "initial_ED_ml", "temporal_role": "UNKNOWN",
             "evidence": "first imaging must not be presumed pre-treatment"},
        ],
        post_exposure_variables=["mrs90", "HM_change_per_10ml", "followup_response"],
        group_structure=group_structure_contract(data, entity_key="patient_id", validation_unit="ENTITY"),
        temporal_structure={"status": "PASS", "purpose": "RETROSPECTIVE_ASSOCIATION",
                            "evidence": "actual imaging-time lookup; initial/current source times <= each response visit",
                            "future_information_used": False, "post_horizon_records_used": 0,
                            "exposure_availability_at_visit": "UNVERIFIED; episode-level recorded treatment indicator",
                            "time_coordinate": "z=log(1+onset_hours/24)-log(8), not time since treatment"},
        estimand=("equal-entity weighted, retrospective conditional ED progression associations with joint HM/recorded treatments"
                  if joint else "recorded-treatment group difference in fitted ED trajectory change from day 7 to day 28"),
        claim_level="ADJUSTED_ASSOCIATION",
        joint_variables=[{"name": name, "role": "JOINT_ASSOCIATION_VARIABLE", "availability": "AT_OR_BEFORE_OUTCOME",
                          "evidence": "matched initial/current imaging serials and row-wise time gate",
                          "relative_to_treatment": "UNVERIFIED; not a confounder or a causal mediator estimate"}
                         for name in ("initial_HM_per_10ml", "HM_change_per_10ml")] if joint else [],
    )


def _record(experiment_id, protocol):
    return {"run_id": RUN_ID, "experiment_id": experiment_id, "created_at": datetime.now(timezone.utc).isoformat(),
            "problem": "2023E", "question": "Q2d" if experiment_id == "Q2D-JOINT" else "Q2c",
            "status": "RUNNING", "updated_by_workflow": "validate_model", "planned_protocol": protocol,
            "executed_protocol": copy.deepcopy(protocol), "protocol_changed": False, "change_reason": "",
            "comparable_to_original_plan": True, "input_artifacts": list(INPUTS),
            "code_artifacts": ["targeted-code", "association-code", "source-reader", "temporal-code", "group-code", "provenance-code"],
            "output_artifacts": [experiment_id + "-output"], "evidence_ids": [experiment_id + "-evidence"],
            "random_seed": None, "metrics": {}}


def _fit(data, contract, output, experiment_id):
    protocol = {"association_analysis": True, "purpose": "RETROSPECTIVE_ASSOCIATION_ESTIMATION",
                "method": "equal-entity WLS, CR1 covariance, t(n_entities-1) nominal intervals",
                "exposures": contract["exposure"], "outcome": contract["outcome"],
                "adjustment": ADJUSTMENT, "joint_variables": [item["name"] for item in contract["joint_variables"]],
                "time_basis": "fixed log1p(days) centered at day 7 plus square", "exposure_time_interactions": "one linear z interaction per exposure",
                "predictive_validation_claim": False, "propensity_used": False, "model_search": False}
    planned_scope = {"claim_level": contract["claim_level"], "adjustment_variables": ADJUSTMENT,
                     "dependence_handling": "ENTITY_CLUSTERED", "analyzed_entity_ids": data["patient_id"].tolist(),
                     "n_rows": len(data), "n_entities": data["patient_id"].nunique(), "fit_row_ids": data.index.tolist()}
    record = apply_association_gate(_record(experiment_id, protocol), contract, planned_scope)
    assert validate_experiment_record(record) == []
    _write(output / (experiment_id + "-record.json"), record)
    result = fit_crude_adjusted_association(data, contract, adjustment_variables=ADJUSTMENT,
                                          time_column=TIME, quadratic_time=True, time_interaction=True)
    record = apply_association_gate(record, contract, result["scope"])
    assert record["status"] == "RUNNING"
    record["status"] = "OBSERVED"
    assert validate_experiment_record(record) == []
    _write(output / (experiment_id + "-record.json"), record)
    _write(output / (experiment_id + "-output.json"), result)
    return result, record


def _trajectory_contrast(result, exposure):
    multiplier = float(np.log1p(28) - np.log1p(7))
    contrast = {}
    for model in ("crude", "adjusted"):
        coefficient = result[model]["coefficients"][exposure + ":" + TIME]
        contrast[model] = {"estimate_ml": coefficient["estimate"] * multiplier,
                           "ci95_ml": [bound * multiplier for bound in coefficient["ci95"]]}
    return {"definition": "recorded-treated minus recorded-untreated difference in fitted ED change, day 7 to day 28; other modeled covariates held fixed",
            **contrast, "coefficient_change_ml": contrast["adjusted"]["estimate_ml"] - contrast["crude"]["estimate_ml"]}


def _plot_q2c(summary, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    short_names = ["Ventricular drainage", "Hemostatic", "Intracranial-pressure treatment", "Antihypertensive",
                   "Sedation / analgesia", "Antiemetic / gastroprotection", "Neurotrophic"]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    positions = np.arange(len(TREATMENTS))
    for model, offset, color in [("crude", -.12, "#898989"), ("adjusted", .12, "#176579")]:
        values = [summary[name]["trajectory_contrast"][model] for name in TREATMENTS]
        centers = np.array([item["estimate_ml"] for item in values])
        low = np.array([item["ci95_ml"][0] for item in values])
        high = np.array([item["ci95_ml"][1] for item in values])
        ax.errorbar(centers, positions + offset, xerr=[centers - low, high - centers], fmt="o",
                    color=color, markersize=4, capsize=3, linewidth=1.3, label=model.capitalize())
    labels = []
    for name, title in zip(TREATMENTS, short_names):
        item = summary[name]["support"]
        star = " *" if item["status"] == "ESTIMATE_UNSTABLE" else ""
        labels.append(f"{title}{star} ({item['treated_n']}/{item['untreated_n']})")
    ax.set_yticks(positions, labels)
    ax.invert_yaxis()
    ax.axvline(0, color="#444444", linewidth=.8, linestyle="--")
    ax.set_xlabel("Difference in fitted ED trajectory change, day 7 to day 28 (mL)")
    ax.set_title("Recorded treatment and edema trajectory: association only", loc="left", pad=18)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", alpha=.18)
    ax.legend(loc="upper right", frameon=False)
    fig.text(.02, .035, "Nominal 95% entity-cluster intervals; 100 entities. Labels: treated/untreated.\n"
             "* One comparison arm has fewer than 10 entities. Treatment timing is unverified.", fontsize=9)
    fig.tight_layout(rect=(0, .10, 1, 1))
    fig.savefig(output / "q2c-crude-adjusted.png", dpi=160)
    plt.close(fig)


def run_targeted(output: Path):
    output = output.resolve()
    if any(output.is_relative_to(root.resolve()) for root in [PROJECT / "skill", PROJECT / "development/benchmarks"]):
        raise ValueError("targeted artifacts must not enter Skill or frozen historical sources")
    if output == PROJECT:
        raise ValueError("use a dedicated development artifact directory")
    if output.is_relative_to(PROJECT) and not any(output.is_relative_to(root) for root in (PROJECT / ".tmp", PROJECT / "development/artifacts")):
        raise ValueError("repository outputs belong in .tmp or development/artifacts")
    output.mkdir(parents=True, exist_ok=True)
    source_hashes = {name: _sha(path) for name, path in INPUTS.items()}
    _write(output / "workspace-manifest.json", {
        "run_id": RUN_ID, "active_run_id": RUN_ID, "allowed_write_root": str(output),
        "allowed_read_files": [str(path) for path in [*INPUTS.values(), READER]],
        "frozen_sources_read_only": True, "historical_code_reused_read_only": str(READER),
        "clean_room_claim": False, "purpose": "development Q2c/Q2d targeted association analysis",
        "input_sha256": source_hashes,
    })
    observations, clinical_columns, availability = _read_data()
    audit = audit_exposures(observations, TREATMENTS, outcome="ED_ml", entity_key="patient_id",
                            baseline_variables=["age", "male", "hypertension", "pre_mrs", "initial_HM_ml", "initial_ED_ml"])
    timing = {"assignment_type": "OBSERVATIONAL", "status": "EXPOSURE_TIME_UNVERIFIED",
              "clinical_source_columns": clinical_columns, "exposure_fields": dict(zip(TREATMENTS, LABELS)),
              "reason": "the treatment indicators have no documented event timestamps; imaging timestamps do not establish treatment ordering",
              "verified_pre_exposure_adjustment": ADJUSTMENT,
              "initial_measurements_are_not_verified_confounders": ["initial_HM_ml", "initial_ED_ml", "blood_pressure"],
              "pre_mrs_not_adjusted": "96 of 100 are zero; keep the adjustment set small and prespecified",
              "remaining_confounding": "acute severity and co-interventions remain incompletely controlled"}
    _write(output / "exposure-audit.json", audit)
    _write(output / "timing-audit.json", timing)
    _write(output / "source-time-gates.json", availability)

    q2c, records = {}, []
    for exposure in TREATMENTS:
        contract = _contract(observations, [exposure], "ED_ml")
        result, record = _fit(observations, contract, output, "Q2C-" + exposure)
        q2c[exposure] = {"label": LABELS[TREATMENTS.index(exposure)],
                         "support": audit["exposures"][exposure],
                         "trajectory_contrast": _trajectory_contrast(result, exposure),
                         "claim_level": result["claim_level"], "n_entities": result["adjusted"]["n_entities"],
                         "n_rows": result["adjusted"]["n_rows"], "warnings": result["warnings"]}
        records.append(record)
    # Select only by exposure support and co-occurrence, never by outcomes,
    # p-values or fitted associations. No combinatorial treatment model search.
    eligible = [name for name in TREATMENTS if audit["exposures"][name]["status"] == "SUPPORTED_FOR_EXPLORATION"]
    eligible.sort(key=lambda name: (-min(audit["exposures"][name]["treated_n"], audit["exposures"][name]["untreated_n"]), name))
    selected = []
    for name in eligible:
        if not any(pair["highly_correlated"] and name in (pair["left"], pair["right"])
                   and any(other in (pair["left"], pair["right"]) for other in selected) for pair in audit["cooccurrence"]):
            selected.append(name)
        if len(selected) == 2:
            break
    followup = observations[observations["visit_index"] > 0].copy()
    assert len(followup) == 350 and followup["patient_id"].nunique() == 100
    joint_contract = _contract(followup, selected, "ED_change_ml", joint=True)
    result, record = _fit(followup, joint_contract, output, "Q2D-JOINT")
    records.append(record)
    q2d = {"selected_treatments": selected,
           "selection_rule": "at most two largest min(treated,untreated) entity counts, each arm >=10, pairwise |phi|<0.85; no outcome use",
           "outcome": "ED change from the first image in mL, follow-up rows only",
           "n_entities": result["adjusted"]["n_entities"], "n_rows": result["adjusted"]["n_rows"],
           "n_parameters_adjusted": result["adjusted"]["n_parameters"],
           "HM_coefficients": {name: {model: result[model]["coefficients"][name] for model in ("crude", "adjusted")}
                               for name in ("initial_HM_per_10ml", "HM_change_per_10ml")},
           "treatment_trajectory_contrasts": {name: _trajectory_contrast(result, name) for name in selected},
           "interpretation": "joint conditional observed associations; HM measurements are study variables, not verified pre-treatment confounders",
           "claim_level": "ADJUSTED_ASSOCIATION", "warnings": result["warnings"]}
    wording = {
        "unsupported": review_association_claim("治疗导致水肿进展减缓；该治疗有效降低水肿体积。", joint_contract),
        "supported": review_association_claim("控制年龄、性别及高血压病史后，观察到血肿变化与水肿变化的条件关联；不能证明治疗导致变化。", joint_contract),
    }
    summary = {"run_id": RUN_ID, "analysis_status": "OBSERVATIONAL_ASSOCIATION_ONLY",
               "volume_unit": "mL (raw 10^-3 mL / 1000)", "Q2c": q2c, "Q2d": q2d,
               "timing": timing, "causal_claim_reviewer": wording,
               "independent_units": 100, "intervals": "nominal 95% CR1, t(99); exploratory, not multiplicity-adjusted",
               "predictive_validation_claim": False, "robustness_sensitivity_performed": False,
               "Q1_Q3_rerun": False, "remaining_modeling_risks": ["robustness / sensitivity"]}
    _write(output / "results.json", summary)
    _plot_q2c(q2c, output)
    observations.drop(columns=["timestamp"]).to_csv(output / "analysis-rows.csv", index=True, index_label="row_id")
    _write(output / "active-evidence-set.json", {"run_id": RUN_ID,
        "active_evidence_set": {record["experiment_id"]: {"run_id": RUN_ID, "experiment_id": record["experiment_id"],
                                                        "artifact": record["output_artifacts"][0]}
                                for record in records}})
    codes = {"targeted-code": Path(__file__).resolve(), "source-reader": READER,
             "association-code": PROJECT / "skill/scripts/association_analysis.py",
             "temporal-code": PROJECT / "skill/scripts/temporal_availability.py",
             "group-code": PROJECT / "skill/scripts/group_validation.py",
             "provenance-code": PROJECT / "skill/scripts/runtime_provenance.py"}
    artifacts = {**INPUTS, **codes, **{path.stem: path for path in output.iterdir() if path.is_file() and path.name != "evidence-ledger.json"}}
    _write(output / "evidence-ledger.json", {"run_id": RUN_ID,
        "artifacts": [{"artifact_id": name, "path": str(path.resolve()), "sha256": _sha(path)} for name, path in artifacts.items()],
        "evidence": [{"evidence_id": record["evidence_ids"][0], "experiment_id": record["experiment_id"],
                      "run_id": RUN_ID, "artifact_id": record["output_artifacts"][0], "status": record["status"]}
                     for record in records]})
    assert source_hashes == {name: _sha(path) for name, path in INPUTS.items()}
    return summary


@pytest.fixture(scope="module")
def targeted(tmp_path_factory):
    output = tmp_path_factory.mktemp("association-q2-targeted")
    return run_targeted(output), output


def test_all_seven_exposures_audited_at_entity_level(targeted):
    results, output = targeted
    audit = json.loads((output / "exposure-audit.json").read_text(encoding="utf-8"))
    assert audit["n_entities"] == 100 and audit["n_rows"] == 450
    assert len(audit["cooccurrence"]) == 21
    assert set(results["Q2c"]) == set(TREATMENTS)
    assert sum(item["support"]["status"] == "ESTIMATE_UNSTABLE" for item in results["Q2c"].values()) == 4
    for item in results["Q2c"].values():
        assert item["support"]["treated_n"] + item["support"]["untreated_n"] == 100
        assert "initial_HM_ml" in item["support"]["baseline"]


def test_q2c_crude_adjusted_and_timing_boundaries(targeted):
    results, _ = targeted
    assert results["timing"]["status"] == "EXPOSURE_TIME_UNVERIFIED"
    for item in results["Q2c"].values():
        assert item["claim_level"] == "ADJUSTED_ASSOCIATION"
        assert (item["n_rows"], item["n_entities"]) == (450, 100)
        assert "EXPOSURE_TIME_UNVERIFIED" in item["warnings"]
        for model in ("crude", "adjusted"):
            contrast = item["trajectory_contrast"][model]
            assert np.isfinite(contrast["estimate_ml"])
            assert contrast["ci95_ml"][0] <= contrast["estimate_ml"] <= contrast["ci95_ml"][1]


def test_q2d_small_joint_model_and_hm_roles(targeted):
    results, output = targeted
    joint = results["Q2d"]
    assert joint["selected_treatments"] == ["intracranial_pressure", "hemostatic"]
    assert (joint["n_rows"], joint["n_entities"], joint["n_parameters_adjusted"]) == (350, 100, 12)
    record = json.loads((output / "Q2D-JOINT-record.json").read_text(encoding="utf-8"))
    contract = record["association_contract"]
    assert record["association_scope"]["adjustment_variables"] == ADJUSTMENT
    assert {item["name"] for item in contract["joint_variables"]} == {"initial_HM_per_10ml", "HM_change_per_10ml"}
    with pytest.raises(AssociationAnalysisError, match="CONFOUNDER_TIME_UNVERIFIED|POST_EXPOSURE_ADJUSTMENT"):
        require_association_contract(contract, adjustment_variables=[*ADJUSTMENT, "initial_HM_per_10ml"])


def test_temporal_sources_and_clustered_uncertainty_have_provenance(targeted):
    results, output = targeted
    rows = json.loads((output / "source-time-gates.json").read_text(encoding="utf-8"))
    assert len(rows) == 450
    assert all(row["initial_time_h"] <= row["outcome_time_h"] == row["concurrent_HM_time_h"] for row in rows)
    for path in output.glob("Q2*-output.json"):
        result = json.loads(path.read_text(encoding="utf-8"))
        assert result["adjusted"]["df"] == 99
        assert result["adjusted"]["uncertainty_unit"] == "ENTITY"
        assert result["adjusted"]["predictive_validation_performed"] is False
    assert not results["Q1_Q3_rerun"] and not results["robustness_sensitivity_performed"]


def test_q2_causal_wording_and_records(targeted):
    results, output = targeted
    assert results["causal_claim_reviewer"]["unsupported"]["status"] == "INVALIDATED"
    assert results["causal_claim_reviewer"]["supported"]["status"] == "PASS"
    paths = list(output.glob("Q2*-record.json"))
    assert len(paths) == 8
    for path in paths:
        record = json.loads(path.read_text(encoding="utf-8"))
        assert record["status"] == "OBSERVED" and validate_experiment_record(record) == []


def test_targeted_outputs_have_matching_evidence_hashes(targeted):
    _, output = targeted
    ledger = json.loads((output / "evidence-ledger.json").read_text(encoding="utf-8"))
    artifacts = {item["artifact_id"]: item for item in ledger["artifacts"]}
    assert len(artifacts) == len(ledger["artifacts"])
    assert (output / "q2c-crude-adjusted.png").stat().st_size > 1000
    for item in artifacts.values():
        assert _sha(item["path"]) == item["sha256"]
    for evidence in ledger["evidence"]:
        assert evidence["artifact_id"] in artifacts and evidence["status"] == "OBSERVED"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    summary = run_targeted(args.output)
    print(json.dumps({"status": summary["analysis_status"], "independent_units": summary["independent_units"],
                      "Q2c_models": len(summary["Q2c"]), "Q2d_selected_treatments": summary["Q2d"]["selected_treatments"]}))
