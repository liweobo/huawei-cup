"""2022C structured-improvement regression.

The initial incumbent is the run-002 feasible source-order schedule. The
move family changes the *real vehicle sequence* by bounded adjacent swaps,
then realizes every candidate through the complete frozen PBS event loop
and evaluates the true objective. No abstract permutation surrogate can
update the incumbent.
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
RUN_003 = BENCH_ROOT / "run-003-postfix"
MODEL_SOURCE = RUN_002 / "code" / "pbs_model.py"
MODEL_COPY = RUN_ROOT / "frozen_model_copy.py"
INPUT = RUN_002 / "inputs-raw" / "attachment1.xlsx"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_model():
    spec = importlib.util.spec_from_file_location("structured_pbs_model", MODEL_COPY)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load structured PBS model")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def candidate_orders(model, vehicles):
    """Adjacent-swap move family over the real vehicle sequence.

    This is a bounded first-improvement neighborhood: only adjacent swaps
    in the source list are considered, then each candidate is fully decoded
    by the PBS event loop.
    """
    for index in range(len(vehicles) - 1):
        candidate = vehicles.copy()
        candidate[index], candidate[index + 1] = candidate[index + 1], candidate[index]
        yield f"adjacent-swap-{index}-{index + 1}", candidate


def evaluate(model, vehicles, scenario):
    dispatcher = model.PBSDispatcher(vehicles, scenario=scenario, strategy="source-order")
    result = dispatcher.run()
    scores = model.detailed_scores(result, dispatcher.vehicle_by_id)
    return dispatcher, result, scores


def export_workbook(path: Path, result, vehicle_count: int):
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
    model = load_model()
    vehicles = model.read_vehicles(INPUT)
    scenario_results = {}
    for scenario, result_name in (("Q1", "result41.xlsx"), ("Q2", "result42.xlsx")):
        started = time.perf_counter()
        initial_vehicles = vehicles.copy()
        initial_dispatcher, initial_result, initial_scores = evaluate(
            model, initial_vehicles, scenario
        )
        incumbent_dispatcher, incumbent_result = initial_dispatcher, initial_result
        incumbent_score = initial_scores["weighted_score"]
        working_vehicles = initial_vehicles.copy()
        working_score = incumbent_score
        trace = []
        evaluated = 0
        feasible_moves = 0
        accepted_moves = 0
        max_evaluations = 24
        for move_name, candidate_vehicles in candidate_orders(model, vehicles):
            if evaluated >= max_evaluations:
                break
            evaluated += 1
            candidate_dispatcher, candidate_result, candidate_scores = evaluate(
                model, candidate_vehicles, scenario
            )
            feasible = candidate_result.feasible and candidate_dispatcher.violations == []
            before = incumbent_score
            accepted = False
            reason = "infeasible candidate rejected"
            if feasible:
                feasible_moves += 1
                candidate_score = candidate_scores["weighted_score"]
                if candidate_score > incumbent_score:
                    incumbent_dispatcher = candidate_dispatcher
                    incumbent_result = candidate_result
                    incumbent_score = candidate_score
                    working_vehicles = candidate_vehicles
                    working_score = candidate_score
                    accepted = True
                    accepted_moves += 1
                    reason = "real objective improved"
                else:
                    reason = "real objective not improved"
            trace.append(
                {
                    "iteration": evaluated,
                    "move_family": "adjacent_swap",
                    "candidate_id": move_name,
                    "feasible": feasible,
                    "objective": candidate_scores["weighted_score"],
                    "incumbent_before": before,
                    "incumbent_after": incumbent_score,
                    "accepted": accepted,
                    "reason": reason,
                }
            )
        runtime = time.perf_counter() - started
        output_dir = RUN_ROOT / "outputs" / scenario.lower()
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "scores.json").write_text(
            json.dumps(model.detailed_scores(incumbent_result, incumbent_dispatcher.vehicle_by_id), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (output_dir / "search-trace.json").write_text(
            json.dumps(trace, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (output_dir / "solver-log.json").write_text(
            json.dumps(
                {
                    "candidate_representation": "STATE_COUPLED",
                    "structured_improvement": True,
                    "move_families": [
                        {
                            "name": "adjacent_swap",
                            "decision_component": "vehicle sequence positions",
                            "rationale": "changes pair/block structure before real PBS decoding",
                            "applicability": "adjacent source-order vehicles",
                            "expected_effect": "improve O1/O2 while preserving hard PBS constraints",
                        }
                    ],
                    "initial_incumbent_score": initial_scores["weighted_score"],
                    "final_incumbent_score": incumbent_score,
                    "evaluated_moves": evaluated,
                    "feasible_moves": feasible_moves,
                    "accepted_moves": accepted_moves,
                    "incumbent_updates": accepted_moves,
                    "termination_reason": "max evaluations reached" if evaluated >= max_evaluations else "no more moves",
                    "runtime_seconds": runtime,
                    "hard_violations": len(incumbent_result.violations),
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        export_workbook(RUN_ROOT / "outputs" / result_name, incumbent_result, len(vehicles))
        scenario_results[scenario] = {
            "initial_incumbent_score": initial_scores["weighted_score"],
            "final_incumbent_score": incumbent_score,
            "objective_improved": incumbent_score > initial_scores["weighted_score"],
            "evaluated_moves": evaluated,
            "feasible_moves": feasible_moves,
            "accepted_moves": accepted_moves,
            "incumbent_updates": accepted_moves,
            "hard_violations": len(incumbent_result.violations),
            "runtime_seconds": runtime,
        }
    (RUN_ROOT / "work").mkdir(exist_ok=True)
    (RUN_ROOT / "work" / "comparison.json").write_text(
        json.dumps(
            {
                "benchmark_id": "historical_2022_c_buffer_scheduling",
                "run_id": "run-004-structured-improvement",
                "source_model_sha256": sha256(MODEL_SOURCE),
                "results": scenario_results,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(scenario_results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
