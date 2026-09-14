"""Tests for the data audit module."""

from pathlib import Path

import pandas as pd
import pytest

from skill.scripts.data_audit import audit_file


def test_audit_csv_reports_quality_risks(tmp_path: Path) -> None:
    """CSV audits should expose missing, duplicate and outlier prompts."""
    path = tmp_path / "sample.csv"
    pd.DataFrame(
        {
            "value": [1.0, 2.0, None, 100.0, 1.0],
            "category": ["a", "b", "b", "b", "a"],
            "date": ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04", "2026-01-01"],
        }
    ).to_csv(path, index=False)
    report = audit_file(path)
    sheet = report["sheets"]["<csv>"]
    assert sheet["shape"] == [5, 3]
    assert sheet["columns"]["value"]["missing_count"] == 1
    assert sheet["columns"]["date"]["kind"] == "time_candidate"
    assert any("missing_review" in risk for risk in sheet["risk_prompts"])


def test_audit_header_only_csv_is_empty(tmp_path: Path) -> None:
    """A header-only table should be reported rather than crashing."""
    path = tmp_path / "empty.csv"
    path.write_text("a,b\n", encoding="utf-8")
    report = audit_file(path)
    assert report["sheets"]["<csv>"]["shape"] == [0, 2]
    assert "empty_data: table has no rows" in report["sheets"]["<csv>"]["risk_prompts"]


def test_audit_excel_multiple_sheets(tmp_path: Path) -> None:
    """Excel audit should preserve sheet names."""
    pytest.importorskip("openpyxl")
    path = tmp_path / "book.xlsx"
    with pd.ExcelWriter(path) as writer:
        pd.DataFrame({"x": [1, 2]}).to_excel(writer, sheet_name="data", index=False)
        pd.DataFrame({"y": [3]}).to_excel(writer, sheet_name="meta", index=False)
    assert set(audit_file(path)["sheets"]) == {"data", "meta"}


def test_audit_rejects_unsupported_or_missing_file(tmp_path: Path) -> None:
    """Unsupported and missing files should fail explicitly."""
    missing = tmp_path / "missing.csv"
    with pytest.raises(FileNotFoundError):
        audit_file(missing)
    path = tmp_path / "sample.txt"
    path.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError):
        audit_file(path)


def test_audit_reports_id_constant_imbalance_correlation_and_time_hints(tmp_path: Path) -> None:
    """Audit should expose advisory structural and risk signals."""
    path = tmp_path / "risks.csv"
    pd.DataFrame(
        {
            "record_id": list(range(1, 21)),
            "constant": [7] * 20,
            "mostly_one": ["x"] * 19 + ["y"],
            "class": ["A"] * 19 + ["B"],
            "signal_a": list(range(1, 21)),
            "signal_b": list(range(2, 42, 2)),
            "time": [f"2026-01-{day:02d}" for day in list(range(20, 1, -1)) + [2]],
        }
    ).to_csv(path, index=False)
    sheet = audit_file(path)["sheets"]["<csv>"]
    assert "record_id" in sheet["possible_id_columns"]
    assert "constant" in sheet["constant_columns"]
    assert "mostly_one" in sheet["near_constant_columns"]
    assert sheet["class_distribution"]["class"]["A"] == 19
    assert sheet["imbalance_ratio"]["class"] == pytest.approx(19.0)
    assert any("class_imbalance_hint: class" in risk for risk in sheet["risk_prompts"])
    assert any(set(pair["columns"]) == {"signal_a", "signal_b"} for pair in sheet["high_correlation_pairs"])
    assert sheet["time_columns"] == ["time"]
    assert sheet["is_monotonic"]["time"] is False
    assert sheet["duplicate_timestamps"]["time"] == 1


def test_audit_rejects_legacy_xls_without_claiming_support(tmp_path: Path) -> None:
    """The V2.1 contract supports CSV and .xlsx, not legacy .xls."""
    path = tmp_path / "legacy.xls"
    path.write_bytes(b"not an xls workbook")
    with pytest.raises(ValueError, match=r"csv or \.xlsx"):
        audit_file(path)


def test_declared_numeric_binary_target_reports_majority_baseline(tmp_path: Path) -> None:
    """A numeric 0/1 target should not be missed by categorical heuristics."""
    path = tmp_path / "binary.csv"
    pd.DataFrame({"feature": range(100), "target": [0] * 77 + [1] * 23}).to_csv(
        path, index=False
    )
    contract = audit_file(path, classification_target="target")["sheets"]["<csv>"][
        "classification_target"
    ]
    assert contract["status"] == "PASS"
    assert contract["positive_count"] == 23
    assert contract["negative_count"] == 77
    assert contract["minority_ratio"] == pytest.approx(0.23)
    assert contract["majority_baseline_accuracy"] == pytest.approx(0.77)
    assert contract["accuracy_trap_review"] is True


def test_classification_target_context_fails_closed_when_target_missing(tmp_path: Path) -> None:
    path = tmp_path / "static.csv"
    pd.DataFrame({"x": [1, 2, 3]}).to_csv(path, index=False)
    contract = audit_file(path, classification_target="label")["sheets"]["<csv>"][
        "classification_target"
    ]
    assert contract["status"] == "UNVERIFIED"


def test_audit_reports_repeated_entity_structure_and_validation_unit(tmp_path: Path) -> None:
    path = tmp_path / "repeated.csv"
    pd.DataFrame(
        {"patient_id": ["p1", "p1", "p2", "p2", "p2"], "time": [1, 2, 1, 2, 3], "value": [1, 2, 3, 4, 5]}
    ).to_csv(path, index=False)
    sheet = audit_file(path, group_context={"entity_key": "patient_id", "validation_unit": "ENTITY"})["sheets"]["<csv>"]
    contract = sheet["group_structure"]
    assert contract["status"] == "PASS"
    assert contract["n_entities"] == 2
    assert contract["n_rows"] == 5
    assert contract["min_rows_per_entity"] == 2
    assert contract["median_rows_per_entity"] == pytest.approx(2.5)
    assert contract["max_rows_per_entity"] == 3
    assert contract["repeated_entities"] == 2
    assert contract["validation_unit"] == "ENTITY"


def test_audit_auto_detects_repeated_entity_candidate_but_does_not_guess_unit(tmp_path: Path) -> None:
    path = tmp_path / "candidate.csv"
    pd.DataFrame({"user_id": ["u1", "u1", "u2"], "score": [1, 2, 3]}).to_csv(path, index=False)
    contract = audit_file(path)["sheets"]["<csv>"]["group_structure"]
    assert contract["status"] == "UNVERIFIED"
    assert contract["validation_unit"] == "UNVERIFIED"
    assert "user_id" in contract["candidate_entity_keys"]
    assert contract["n_entities"] == 2
    assert contract["min_rows_per_entity"] == 1
    assert contract["median_rows_per_entity"] == 1.5
    assert contract["max_rows_per_entity"] == 2


@pytest.mark.parametrize("key", ["entity_id", "subject_id", "patient_id", "machine_id", "city_id",
                                  "user_id", "company_id", "athlete_id", "experiment_id", "assetKey"])
def test_group_detection_is_generic_across_entity_domains(tmp_path: Path, key: str) -> None:
    path = tmp_path / "repeated.csv"
    pd.DataFrame({key: ["a", "a", "b", "b"], "value": [1, 2, 3, 4]}).to_csv(path, index=False)
    inferred = audit_file(path)["sheets"]["<csv>"]["group_structure"]
    assert inferred["n_entities"] == 2
    assert inferred["repeated_entities"] == 2
    assert inferred["validation_unit"] != "ROW"
    confirmed = audit_file(path, group_context={"entity_key": key, "prediction_setting": "NEW_ENTITY"})["sheets"]["<csv>"]["group_structure"]
    assert confirmed["status"] == "PASS"
    assert confirmed["validation_unit"] == "ENTITY"


def test_multiple_entity_candidates_report_each_structure_without_guessing(tmp_path: Path) -> None:
    path = tmp_path / "nested.csv"
    pd.DataFrame({"machine_id": ["a", "a", "b", "b"], "site_id": ["x"] * 4}).to_csv(path, index=False)
    contract = audit_file(path)["sheets"]["<csv>"]["group_structure"]
    assert contract["status"] == "UNVERIFIED"
    assert contract["entity_key"] is None
    assert contract["candidate_structures"]["machine_id"]["n_entities"] == 2
    assert contract["candidate_structures"]["site_id"]["n_entities"] == 1


def test_empty_group_table_fails_closed_without_crashing(tmp_path: Path) -> None:
    path = tmp_path / "empty.csv"
    pd.DataFrame(columns=["entity_id", "value"]).to_csv(path, index=False)
    contract = audit_file(path, group_context={"entity_key": "entity_id", "prediction_setting": "NEW_ENTITY"})["sheets"]["<csv>"]["group_structure"]
    assert contract["status"] == "UNVERIFIED"
    assert contract["n_rows"] == 0


def test_known_class_label_is_not_mistaken_for_entity_identity(tmp_path: Path) -> None:
    path = tmp_path / "independent.csv"
    pd.DataFrame({"x": range(4), "class_id": [0, 1, 0, 1]}).to_csv(path, index=False)
    report = audit_file(path, classification_target="class_id")["sheets"]["<csv>"]
    assert report["group_structure"]["validation_unit"] == "ROW"
    assert report["group_structure"]["candidate_entity_keys"] == []


def test_declared_ordinal_context_requires_an_order_source(tmp_path: Path) -> None:
    path = tmp_path / "ordinal.csv"
    pd.DataFrame({"severity": ["low", "medium", "high"]}).to_csv(path, index=False)
    report = audit_file(
        path,
        ordinal_context={
            "target": "severity",
            "ordered_levels": ["low", "medium", "high"],
            "ordering_source": "schema",
        },
    )
    contract = report["sheets"]["<csv>"]["ordinal_target"]
    assert contract["status"] == "PASS"
    missing_source = audit_file(
        path,
        ordinal_context={"target": "severity", "ordered_levels": ["low", "medium", "high"]},
    )["sheets"]["<csv>"]["ordinal_target"]
    assert missing_source["status"] == "UNVERIFIED"
