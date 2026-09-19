from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_blind_simulation as sim

run = Path(__file__).resolve().parents[1]
target = 1e-2
n = 32768
grid = [13.5, 14.0, 14.5, 15.0, 15.5, 16.0, 16.5, 17.0, 17.5, 18.0]
rows = []
for order in ["dispersion_then_phase", "phase_then_dispersion"]:
    for period in [2, 8, 16, 32, 64]:
        threshold = math.nan
        for snr in grid:
            r = sim.simulate(snr_db=snr, lw_khz=100.0, dz_ps_nm=20000.0, period=period, method="linear_smooth3", n=n, seed=202009, channel_order=order)
            if r["ber"] <= target:
                threshold = snr
                break
        rows.append({"channel_order": order, "period": period, "threshold_snr_db_grid": threshold, "target_ber": target})
path = run / "outputs/channel_order_sensitivity.csv"
with path.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(rows)
