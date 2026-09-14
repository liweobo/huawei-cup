"""Verify evaluator-only workbook facts against the registered raw XLSX files."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml
from openpyxl import load_workbook

from trajectory_test import ROOT, validate_source_record


PROBLEM = ROOT / "development/benchmarks/problems/2024/C"
SOURCE = PROBLEM / "source.yaml"
FACTS = PROBLEM / "problem-facts.yaml"
MANIFEST = PROBLEM / "extracted/attachments-manifest.yaml"


def check(label: str, ok: bool, failures: list[str]) -> None:
    print(f"{'PASS' if ok else 'FAIL'} | {label}")
    if not ok:
        failures.append(label)


def load(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return value


def workbook_observation(path: Path) -> dict[str, Any]:
    """Read dimensions and first-row headers without loading cell bodies."""
    workbook = load_workbook(path, read_only=True, data_only=False)
    sheets: list[dict[str, Any]] = []
    try:
        for worksheet in workbook.worksheets:
            headers = [worksheet.cell(1, column).value for column in range(1, worksheet.max_column + 1)]
            sheets.append({
                "name": worksheet.title,
                "rows": worksheet.max_row,
                "columns": worksheet.max_column,
                "headers": headers,
            })
    finally:
        workbook.close()
    return {"sheets": sheets}


def has_header(headers: list[Any], text: str) -> bool:
    return any(str(value).strip() == text for value in headers if value is not None)


def header_starts_with(headers: list[Any], text: str) -> bool:
    return any(str(value).strip().startswith(text) for value in headers if value is not None)


def main() -> int:
    failures: list[str] = []
    source = load(SOURCE)
    facts = load(FACTS)
    manifest = load(MANIFEST)
    source_items = {item["id"]: item for item in source.get("artifacts", [])}
    fact_items = {item["artifact_id"]: item for item in facts.get("facts", {}).get("observed_files", [])}
    manifest_items = {item["artifact_id"]: item for item in manifest.get("attachments", [])}
    expected_files = {
        "ART-002": {"rows": [3401, 3001, 3201, 2801], "columns": 1028, "sheets": ["材料1", "材料2", "材料3", "材料4"]},
        "ART-003": {"rows": [81], "columns": 1028, "sheets": ["测试集"]},
        "ART-004": {"rows": [401], "columns": 1029, "sheets": ["测试集"]},
        "ART-005": {"rows": [401, 1, 1], "columns": [3, 1, 1], "sheets": ["Sheet1", "Sheet2", "Sheet3"]},
    }

    source_xlsx_ids = {artifact_id for artifact_id, item in source_items.items() if item.get("type") == "XLSX"}
    fact_xlsx_ids = {artifact_id for artifact_id, item in fact_items.items() if str(item.get("filename", "")).endswith(".xlsx")}
    check("source manifest hashes and raw files are valid", not validate_source_record(SOURCE, "ACCEPTED"), failures)
    check("facts and extracted manifest cover all XLSX source artifacts", set(expected_files) == source_xlsx_ids == fact_xlsx_ids == set(manifest_items), failures)

    for artifact_id, expected in expected_files.items():
        source_item = source_items.get(artifact_id, {})
        filename = source_item.get("filename")
        raw_path = PROBLEM / str(source_item.get("raw_path", ""))
        observed = workbook_observation(raw_path) if raw_path.exists() else {"sheets": []}
        sheets = observed["sheets"]
        check(f"{artifact_id} raw workbook exists", raw_path.exists(), failures)
        check(f"{artifact_id} sheet names match raw workbook", [sheet["name"] for sheet in sheets] == expected["sheets"], failures)
        check(f"{artifact_id} row dimensions match raw workbook", [sheet["rows"] for sheet in sheets] == expected["rows"], failures)
        expected_columns = expected["columns"] if isinstance(expected["columns"], int) else expected["columns"]
        check(f"{artifact_id} column dimensions match raw workbook", [sheet["columns"] for sheet in sheets] == ([expected_columns] * len(sheets) if isinstance(expected_columns, int) else expected_columns), failures)

        fact = fact_items.get(artifact_id, {})
        manifest_item = manifest_items.get(artifact_id, {})
        check(f"{artifact_id} role is consistent across source/facts/manifest", source_item.get("role") == fact.get("role") == manifest_item.get("role"), failures)
        check(f"{artifact_id} filename is consistent across source/facts/manifest", filename == fact.get("filename") == manifest_item.get("filename"), failures)

        manifest_sheets = manifest_item.get("observed_sheets", [])
        check(f"{artifact_id} manifest dimensions match raw workbook", [item.get("data_rows", 0) + 1 for item in manifest_sheets] == [sheet["rows"] for sheet in sheets] and [item.get("columns") for item in manifest_sheets] == [sheet["columns"] for sheet in sheets], failures)

        if artifact_id == "ART-002":
            check("ART-002 headers expose target, waveform, and flux samples", all(has_header(sheet["headers"], "励磁波形") and header_starts_with(sheet["headers"], "磁芯损耗") for sheet in sheets), failures)
        elif artifact_id == "ART-003":
            headers = sheets[0]["headers"] if sheets else []
            check("ART-003 has no excitation-waveform label column", not has_header(headers, "励磁波形"), failures)
            check("ART-003 has flux-density sample columns", header_starts_with(headers, "0（磁通密度"), failures)
        elif artifact_id == "ART-004":
            headers = sheets[0]["headers"] if sheets else []
            check("ART-004 contains excitation-waveform label column", has_header(headers, "励磁波形"), failures)
            check("ART-004 has flux-density sample columns", header_starts_with(headers, "0（磁通密度"), failures)
        elif artifact_id == "ART-005":
            headers = sheets[0]["headers"] if sheets else []
            check("ART-005 Sheet1 has the two required output columns", len(headers) == 3 and "附件二" in str(headers[1]) and "附件三" in str(headers[2]), failures)

    fact_dims = facts.get("facts", {}).get("workbook_dimensions", {})
    check("problem-facts attachment_1 dimensions match all four sheets", fact_dims.get("attachment_1") == {"sheets": 4, "rows_by_sheet": [3401, 3001, 3201, 2801], "columns_observed": 1028}, failures)
    check("problem-facts attachment_2 dimensions are 81x1028", fact_dims.get("attachment_2") == {"rows": 81, "columns_observed": 1028}, failures)
    check("problem-facts attachment_3 dimensions are 401x1029", fact_dims.get("attachment_3") == {"rows": 401, "columns_observed": 1029}, failures)
    check("problem-facts attachment_4 Sheet1 dimensions are 401x3", fact_dims.get("attachment_4") == {"sheet1_rows": 401, "sheet1_columns": 3}, failures)
    fact_columns = facts.get("facts", {}).get("existing_columns", {})
    check("problem-facts attachment_2 omits waveform label", "excitation_waveform" not in fact_columns.get("attachment_2", []), failures)
    check("problem-facts attachment_3 includes waveform label", "excitation_waveform" in fact_columns.get("attachment_3", []), failures)

    total = 42
    print(f"\nProblem Facts Regression: {'PASS' if not failures else 'FAIL'} ({total - len(failures)}/{total} checks)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
