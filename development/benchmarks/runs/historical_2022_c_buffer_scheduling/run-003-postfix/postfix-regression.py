"""State-coupled post-fix regression for the frozen 2022C PBS problem.

The complete event loop, transition functions, hard invariants, and terminal
test are copied from run-002, then exposed through an additive
``action_policy`` hook. Only legal actions returned by the current PBS state
can be selected. The resulting schedule is exported and independently audited.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import time
from pathlib import Path

from openpyxl import Workbook


RUN_ROOT = Path(__file__).resolve().parent
BENCH_ROOT = RUN_ROOT.parent
RUN_002 = BENCH_ROOT / "run-002"
MODEL_SOURCE = RUN_002 / "code" / "pbs_model.py"
MODEL_COPY = RUN_ROOT / "frozen_model_copy.py"
INPUT_DIR = RUN_002 / "inputs-raw"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_model():
    spec = importlib.util.spec_from_file_location("stateful_pbs_model", MODEL_COPY)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load state-coupled PBS model")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def action_priority(dispatcher, action):
    """Prioritize a legal action using the current real output state."""
    kind, lane, vehicle_id = action
    vehicle = dispatcher.vehicle_by_id[vehicle_id]
    recent = [dispatcher.vehicle_by_id[item] for item in dispatcher.output_order[-3:]]
    hybrid_recent = sum(item.power == "\u6df7\u52a8" for item in recent)
    four_recent = sum(item.drive == "\u56db\u9a71" for item in recent)
    two_recent = sum(item.drive == "\u4e24\u9a71" for item in recent)
    if kind == "to_assembly":
        value = 0.0
        if vehicle.power == "\u6df7\u52a8":
            value += 8.0 if hybrid_recent != 2 else -3.0
        else:
            value += 3.0 if hybrid_recent == 2 else -1.0
        if vehicle.drive == "\u56db\u9a71":
            value += 4.0 if four_recent < two_recent else -1.5
        else:
            value += 4.0 if two_recent < four_recent else -1.5
        return value - 0.05 * lane
    if kind == "to_return":
        # Returning a body is useful only when the immediately following
        # assembly candidate is clearly inconsistent with the current run.
        if not dispatcher.output_order:
            return -100.0
        next_candidate = dispatcher._lane_position_one_candidate()
        if next_candidate is None:
            return -100.0
        next_vehicle = dispatcher.vehicle_by_id[next_candidate[1]]
        if next_vehicle.power == vehicle.power:
            return -2.0
        return -100.0
    return -100.0


def make_policy(trace, model):
    returned_vehicle_ids = set()

    def policy(dispatcher):
        legal = dispatcher.legal_delivery_actions()
        legal = [
            action
            for action in legal
            if not (
                action[0] == "to_return"
                and action[2] in returned_vehicle_ids
            )
        ]
        if not legal:
            return None
        # Return-lane position 10 must be drained when it is the only way to
        # make progress; otherwise the finite return lane becomes a deadlock.
        if (
            dispatcher.scenario == "Q1"
            and dispatcher.return_lane
            and dispatcher._can_receive()
        ):
            for action in legal:
                if action[0] == "return_to_lane":
                    return action
        ranked = sorted(
            legal,
            key=lambda action: (
                action_priority(dispatcher, action),
                -action[1],
                -action[2],
            ),
            reverse=True,
        )
        chosen = ranked[0]
        if chosen[0] == "to_return":
            returned_vehicle_ids.add(chosen[2])
        trace.append(
            {
                "time": dispatcher.time,
                "legal_actions": [
                    {"kind": item[0], "lane": item[1], "vehicle_id": item[2]}
                    for item in legal
                ],
                "chosen_action": {
                    "kind": chosen[0],
                    "lane": chosen[1],
                    "vehicle_id": chosen[2],
                },
                "return_occupancy": len(dispatcher.return_lane),
                "output_count": len(dispatcher.output_order),
            }
        )
        return chosen

    return policy


def export_workbook(path: Path, result, vehicle_count: int) -> None:
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Sheet1"
    for second in range(result.completion_time + 1):
        worksheet.cell(row=1, column=second + 2, value=second)
    for row_index, vehicle_id in enumerate(range(1, vehicle_count + 1), start=2):
        worksheet.cell(row=row_index, column=1, value=vehicle_id)
        for second in range(result.completion_time + 1):
            code = result.timeline.get(vehicle_id, {}).get(second)
            if code is not None:
                worksheet.cell(row=row_index, column=second + 2, value=code)
    workbook.save(path)


def main() -> None:
    if sha256(MODEL_COPY) == sha256(MODEL_SOURCE):
        raise RuntimeError("run-003 model copy must contain the additive action hook")
    model = load_model()
    output_root = RUN_ROOT / "outputs"
    output_root.mkdir(parents=True, exist_ok=True)
    comparison = {
        "benchmark_id": "historical_2022_c_buffer_scheduling",
        "run_id": "run-003-postfix",
        "source_model_sha256": sha256(MODEL_SOURCE),
        "stateful_model_copy_sha256": sha256(MODEL_COPY),
        "results": [],
    }
    for scenario, result_name in (("Q1", "result31.xlsx"), ("Q2", "result32.xlsx")):
        source = INPUT_DIR / "attachment1.xlsx"
        vehicles = model.read_vehicles(source)
        trace = []
        started = time.perf_counter()
        dispatcher = model.PBSDispatcher(vehicles, scenario=scenario, strategy="greedy")
        result = dispatcher.run(action_policy=make_policy(trace, model))
        runtime = time.perf_counter() - started
        scores = model.detailed_scores(result, dispatcher.vehicle_by_id)
        target = output_root / f"{scenario.lower()}-state-coupled"
        target.mkdir(parents=True, exist_ok=True)
        (target / "scores.json").write_text(
            json.dumps(scores, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (target / "decision-trace.json").write_text(
            json.dumps(trace, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        solver_log = {
            "candidate_representation": "STATE_COUPLED",
            "feasibility_mode": "BY_CONSTRUCTION",
            "legal_actions": "dispatcher.legal_delivery_actions() on current state",
            "transition": "same complete frozen run-002 event loop",
            "random_seed": None,
            "runtime_seconds": runtime,
            "feasible": result.feasible,
            "hard_violations": len(result.violations),
            "completion_time": result.completion_time,
            "return_use_count": result.return_use_count,
            "weighted_score": scores["weighted_score"],
        }
        (target / "solver-log.json").write_text(
            json.dumps(solver_log, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        export_workbook(output_root / result_name, result, len(vehicles))
        comparison["results"].append(
            {
                "scenario": scenario,
                "candidate_representation": "STATE_COUPLED",
                "feasible": result.feasible,
                "hard_violations": len(result.violations),
                "weighted_score": scores["weighted_score"],
                "objective_1": scores["objective_1"]["score"],
                "objective_2": scores["objective_2"]["score"],
                "objective_3": scores["objective_3"]["score"],
                "objective_4": scores["objective_4"]["score"],
                "runtime_seconds": runtime,
            }
        )
    (RUN_ROOT / "work").mkdir(exist_ok=True)
    (RUN_ROOT / "work" / "comparison.json").write_text(
        json.dumps(comparison, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(comparison, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
