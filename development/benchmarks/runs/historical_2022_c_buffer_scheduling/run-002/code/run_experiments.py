"""Run the 2022 C PBS baselines and deterministic greedy candidates."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

import numpy
import openpyxl

from pbs_model import (
    PBSDispatcher,
    detailed_scores,
    export_result_workbook,
    read_vehicles,
    write_json,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_one(
    scenario: str,
    strategy: str,
    attachment: Path,
    output_root: Path,
) -> dict:
    vehicles = read_vehicles(attachment)
    start = time.perf_counter()
    dispatcher = PBSDispatcher(vehicles, scenario=scenario, strategy=strategy)
    result = dispatcher.run()
    runtime = time.perf_counter() - start
    scores = detailed_scores(result, dispatcher.vehicle_by_id)
    label = f"{scenario.lower()}-{attachment.stem}-{strategy}"
    result_dir = output_root / label
    result_dir.mkdir(parents=True, exist_ok=True)
    write_json(result_dir / "scores.json", scores)
    write_json(
        result_dir / "solver-log.json",
        {
            "benchmark_id": "historical_2022_c_buffer_scheduling",
            "run_id": "run-002",
            "scenario": scenario,
            "strategy": strategy,
            "solver": "deterministic discrete-event heuristic",
            "version": "run-002-v1",
            "random_seed": None,
            "time_limit_seconds": None,
            "termination": "completed" if result.feasible else "stopped_infeasible",
            "runtime_seconds": runtime,
            "input_sha256": sha256(attachment),
            "vehicle_count": len(vehicles),
            "event_count": len(result.event_log),
            "return_use_count": result.return_use_count,
            "completion_time": result.completion_time,
            "objective_values": {
                key: value["score"] for key, value in scores.items() if key != "weighted_score"
            },
            "weighted_score": scores["weighted_score"],
            "feasible": result.feasible,
            "violations": result.violations,
        },
    )
    write_json(
        result_dir / "events.json",
        result.event_log,
    )
    return {
        "label": label,
        "scenario": scenario,
        "attachment": attachment.name,
        "strategy": strategy,
        "feasible": result.feasible,
        "violations": len(result.violations),
        "output_order": result.output_order,
        "completion_time": result.completion_time,
        "return_use_count": result.return_use_count,
        "scores": scores,
        "runtime_seconds": runtime,
        "result_dir": str(result_dir),
        "result": result,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path)
    args = parser.parse_args()
    run_root = Path(__file__).resolve().parents[1]
    args.output_root = args.output_root or (run_root / "outputs")
    raw_root = run_root / "inputs-raw"

    executions = []
    for scenario in ("Q1", "Q2"):
        for attachment in ("attachment1.xlsx", "attachment2.xlsx"):
            for strategy in ("source-order", "greedy"):
                execution = run_one(
                    scenario,
                    strategy,
                    raw_root / attachment,
                    args.output_root,
                )
                executions.append(execution)
                print(
                    execution["label"],
                    "feasible=",
                    execution["feasible"],
                    "score=",
                    execution["scores"]["weighted_score"],
                )

    summary = {
        "benchmark_id": "historical_2022_c_buffer_scheduling",
        "run_id": "run-002",
        "executions": [
            {
                key: value
                for key, value in execution.items()
                if key != "result"
            }
            for execution in executions
        ],
    }
    write_json(run_root / "work" / "experiment-results.json", summary)
    (run_root / "work" / "solver-provenance.json").write_text(
        json.dumps(
            {
                "python": sys.version,
                "python_executable": sys.executable,
                "platform": platform.platform(),
                "numpy": numpy.__version__,
                "openpyxl": openpyxl.__version__,
                "solver": "in-repo deterministic discrete-event heuristic",
                "random_seed": None,
                "time_limit": None,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    selected = {}
    for execution in executions:
        if not execution["feasible"]:
            continue
        key = (execution["scenario"], execution["attachment"])
        incumbent = selected.get(key)
        if incumbent is None or (
            execution["scores"]["weighted_score"],
            -execution["runtime_seconds"],
        ) > (
            incumbent["scores"]["weighted_score"],
            -incumbent["runtime_seconds"],
        ):
            selected[key] = execution
    result_names = {
        ("Q1", "attachment1.xlsx"): "result11.xlsx",
        ("Q1", "attachment2.xlsx"): "result12.xlsx",
        ("Q2", "attachment1.xlsx"): "result21.xlsx",
        ("Q2", "attachment2.xlsx"): "result22.xlsx",
    }
    for key, filename in result_names.items():
        execution = selected.get(key)
        if execution is None:
            continue
        export_result_workbook(
            args.output_root / filename,
            execution["result"],
            len(execution["result"].output_order),
        )

    print(
        json.dumps(
            {
                "selected": [
                    {
                        "scenario": key[0],
                        "attachment": key[1],
                        "label": value["label"],
                        "score": value["scores"]["weighted_score"],
                    }
                    for key, value in sorted(selected.items())
                ]
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
