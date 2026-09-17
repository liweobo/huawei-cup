"""Create a compact, machine-readable summary of the selected formal results."""

from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    run_root = Path(__file__).resolve().parents[1]
    results = json.loads(
        (run_root / "work" / "experiment-results.json").read_text(encoding="utf-8")
    )
    selected = {}
    for execution in results["executions"]:
        key = (execution["scenario"], execution["attachment"])
        if not execution["feasible"]:
            continue
        incumbent = selected.get(key)
        if incumbent is None or execution["scores"]["weighted_score"] > incumbent[
            "scores"
        ]["weighted_score"]:
            selected[key] = execution
    summary = {
        "benchmark_id": "historical_2022_c_buffer_scheduling",
        "run_id": "run-002",
        "selection_rule": "highest weighted score among feasible candidates under identical problem definition",
        "results": [],
    }
    for (scenario, attachment), execution in sorted(selected.items()):
        scores = execution["scores"]
        summary["results"].append(
            {
                "scenario": scenario,
                "attachment": attachment,
                "selected_strategy": execution["strategy"],
                "feasible": execution["feasible"],
                "hard_violations": execution["violations"],
                "completion_time": execution["completion_time"],
                "return_use_count": execution["return_use_count"],
                "objective_1": scores["objective_1"]["score"],
                "objective_2": scores["objective_2"]["score"],
                "objective_3": scores["objective_3"]["score"],
                "objective_4": scores["objective_4"]["score"],
                "weighted_score": scores["weighted_score"],
            }
        )
    (run_root / "work" / "selected-results.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
