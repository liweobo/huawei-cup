"""Independent audits of exported 2022 C result workbooks."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from openpyxl import load_workbook

from pbs_model import CODE_ASSEMBLY, CODE_INBOUND, CODE_PAINT_EXIT, CODE_RECEIVE, CODE_RETURN, CODE_DELIVERY


ALLOWED_CODES = (
    {CODE_PAINT_EXIT, CODE_RECEIVE, CODE_DELIVERY, CODE_ASSEMBLY}
    | set(CODE_RETURN.values())
    | set(CODE_INBOUND.values())
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_matrix(path: Path) -> tuple[list[list[int | None]], list[int]]:
    workbook = load_workbook(path, read_only=True, data_only=True)
    worksheet = workbook.worksheets[0]
    rows = [list(row) for row in worksheet.iter_rows(values_only=True)]
    workbook.close()
    seconds = rows[0][1:]
    matrix = [row[1:] for row in rows[1:]]
    return matrix, seconds


def audit_result(path: Path) -> dict:
    matrix, seconds = load_matrix(path)
    vehicle_count = len(matrix)
    time_count = len(seconds)
    failures: dict[str, list[dict]] = {
        "matrix_dimensions": [],
        "allowed_region_codes": [],
        "single_position_occupancy": [],
        "vehicle_id_uniqueness": [],
        "initial_paint_exit": [],
        "final_assembly_receipt": [],
        "completion_time_definition": [],
    }
    if time_count == 0 or any(
        seconds[index] != index for index in range(time_count)
    ):
        failures["matrix_dimensions"].append(
            {"message": "time index is not 0..T", "seconds": seconds[:5]}
        )
    if vehicle_count != len(matrix):
        failures["matrix_dimensions"].append({"message": "row count mismatch"})

    for row_index, row in enumerate(matrix, 1):
        if len(row) != time_count:
            failures["matrix_dimensions"].append(
                {"vehicle_row": row_index, "cells": len(row), "expected": time_count}
            )
        for second, code in enumerate(row):
            if code is not None and code not in ALLOWED_CODES:
                failures["allowed_region_codes"].append(
                    {"vehicle": row_index, "second": second, "code": code}
                )
        if row and row[0] not in (CODE_PAINT_EXIT, CODE_RECEIVE):
            failures["initial_paint_exit"].append(
                {"vehicle": row_index, "code": row[0]}
            )
        if CODE_ASSEMBLY not in row:
            failures["final_assembly_receipt"].append({"vehicle": row_index})
        else:
            first_receipt = row.index(CODE_ASSEMBLY)
            # A sustained receipt region is represented by repeated identical
            # code cells; a later non-assembly code would be a true re-entry.
            if any(
                code is not None and code != CODE_ASSEMBLY
                for code in row[first_receipt + 1 :]
            ):
                failures["final_assembly_receipt"].append(
                    {"vehicle": row_index, "message": "PBS region re-entered after receipt"}
                )
            if first_receipt < 0:
                failures["completion_time_definition"].append({"vehicle": row_index})

    # A position code can belong to only one vehicle in a given second.
    for second in range(time_count):
        occupancy: dict[int, int] = {}
        for vehicle, row in enumerate(matrix, 1):
            code = row[second]
            if code is None:
                continue
            if code in set(CODE_INBOUND.values()) or code in set(CODE_RETURN.values()):
                previous = occupancy.get(code)
                if previous is not None:
                    failures["single_position_occupancy"].append(
                        {
                            "second": second,
                            "code": code,
                            "vehicles": [previous, vehicle],
                        }
                    )
                occupancy[code] = vehicle

    family_checks = {
        "allowed_region_codes": vehicle_count * time_count,
        "single_position_occupancy": sum(
            1
            for row in matrix
            for code in row
            if code in set(CODE_INBOUND.values()) or code in set(CODE_RETURN.values())
        ),
        "vehicle_id_uniqueness": vehicle_count,
        "initial_paint_exit": vehicle_count,
        "final_assembly_receipt": vehicle_count,
        "completion_time_definition": vehicle_count,
    }
    violation_counts = {key: len(value) for key, value in failures.items()}
    return {
        "workbook": path.name,
        "sha256": sha256(path),
        "dimensions": {
            "vehicles": vehicle_count,
            "seconds": time_count,
            "first_second": seconds[0] if seconds else None,
            "last_second": seconds[-1] if seconds else None,
        },
        "checks": family_checks,
        "violations": violation_counts,
        "total_hard_violations": sum(violation_counts.values()),
        "status": "FEASIBLE" if sum(violation_counts.values()) == 0 else "INFEASIBLE",
        "examples": failures,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path)
    args = parser.parse_args()
    run_root = Path(__file__).resolve().parents[1]
    output_root = args.output_root or (run_root / "outputs")
    report = {
        "benchmark_id": "historical_2022_c_buffer_scheduling",
        "run_id": "run-002",
        "results": [],
    }
    for name in ("result11.xlsx", "result12.xlsx", "result21.xlsx", "result22.xlsx"):
        path = output_root / name
        if path.exists():
            report["results"].append(audit_result(path))
    report["all_feasible"] = all(
        item["status"] == "FEASIBLE" for item in report["results"]
    )
    destination = run_root / "work" / "feasibility-audit.json"
    destination.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "files": [item["workbook"] for item in report["results"]],
                "all_feasible": report["all_feasible"],
                "violations": {
                    item["workbook"]: item["total_hard_violations"]
                    for item in report["results"]
                },
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
