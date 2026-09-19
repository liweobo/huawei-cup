from __future__ import annotations

import csv
import json
from pathlib import Path

run = Path(__file__).resolve().parents[1]
summary_path = run / "outputs/results-summary.json"
summary = json.loads(summary_path.read_text(encoding="utf-8"))
rows = []
with (run / "outputs/q2_overhead_grid.csv").open(encoding="utf-8") as f:
    for row in csv.DictReader(f):
        converted = {}
        for key, value in row.items():
            if value == "":
                converted[key] = None
            elif key == "method":
                converted[key] = value
            elif key == "gate_pass":
                converted[key] = value == "True"
            else:
                converted[key] = float(value)
        rows.append(converted)
summary["q2"]["rows"] = rows
summary["q2"]["passing_grid_points"] = sum(1 for row in rows if row["gate_pass"])
summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
