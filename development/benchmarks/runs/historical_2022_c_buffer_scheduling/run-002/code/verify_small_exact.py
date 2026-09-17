"""Small exact checks for score construction and return-lane behavior."""

from __future__ import annotations

import itertools
import json
from pathlib import Path

from pbs_model import Vehicle, objective_1, objective_2


def main() -> None:
    vehicles = [
        Vehicle(1, "A", "\u6df7\u52a8", "\u56db\u9a71", 1),
        Vehicle(2, "B", "\u71c3\u6cb9", "\u4e24\u9a71", 2),
        Vehicle(3, "A", "\u6df7\u52a8", "\u4e24\u9a71", 3),
    ]
    vehicle_by_id = {vehicle.vehicle_id: vehicle for vehicle in vehicles}
    rows = []
    for permutation in itertools.permutations([1, 2, 3]):
        order = list(permutation)
        rows.append(
            {
                "order": order,
                "objective_1": objective_1(order, vehicle_by_id),
                "objective_2": objective_2(order, vehicle_by_id),
            }
        )
    destination = Path(__file__).resolve().parents[1] / "work" / "small-exact-check.json"
    destination.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"permutations_checked": len(rows), "path": str(destination)}))


if __name__ == "__main__":
    main()
