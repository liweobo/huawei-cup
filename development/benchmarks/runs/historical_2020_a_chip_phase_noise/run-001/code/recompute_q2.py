from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_blind_simulation as sim


run = Path(__file__).resolve().parents[1]
summary = json.loads((run / "outputs/results-summary.json").read_text(encoding="utf-8"))
gate_snr = float(summary["q1"]["summary"][0]["gate_snr_db"])
n = int(summary["frame_n"])
method = summary["q1"]["primary"]["method"]
target = float(summary["main_ber_threshold"])
periods = [2, 4, 8, 12, 16, 20, 24, 31, 40, 48, 64, 80, 96, 112, 128]
rows = []
for lw in [10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0, 10000.0]:
    for dz in [0.0, 1000.0, 3000.0, 10000.0]:
        tested = []
        for period in periods:
            row = sim.simulate(snr_db=gate_snr, lw_khz=lw, dz_ps_nm=dz, period=period, method=method, n=n, seed=202009)
            row["gate_pass"] = row["ber"] <= target
            tested.append(row)
        best = min(tested, key=lambda x: x["ber"])
        passed = [x for x in tested if x["gate_pass"]]
        gate = max(passed, key=lambda x: x["period"]) if passed else None
        rows.append({"lw_khz": lw, "dz_ps_nm": dz, "method": method, "gate_snr_db": gate_snr, "target_ber": target, "period": gate["period"] if gate else None, "pilot_overhead": (1.0 / gate["period"] if gate else None), "gate_ber": gate["ber"] if gate else None, "best_effort_period": best["period"], "best_effort_ber": best["ber"], "best_effort_overhead": 1.0 / best["period"], "gate_pass": bool(gate)})
path = run / "outputs/q2_overhead_grid.csv"
with path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0]))
    writer.writeheader(); writer.writerows(rows)
(run / "outputs/q2_best_effort.csv").write_text("\n".join(",".join(str(r[k]) for k in rows[0]) for r in rows), encoding="utf-8")
print(json.dumps({"gate_snr_db": gate_snr, "method": method, "rows": len(rows), "passing_rows": sum(r["gate_pass"] for r in rows)}, indent=2))
