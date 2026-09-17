"""Heuristic target-sequence search coupled to the PBS feasibility simulator.

The search does not call an external optimizer. It constructs score-aware
target permutations, applies bounded adjacent swaps and evaluates each target
through the same discrete-event simulator used by the feasibility audit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

from pbs_model import (
    PBSDispatcher,
    Vehicle,
    detailed_scores,
    export_result_workbook,
    objective_1,
    objective_2,
    objective_3,
    objective_4,
    read_vehicles,
    write_json,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def score_sequence(
    order: list[Vehicle],
    vehicle_by_id: dict[int, Vehicle],
    completion_time: int,
    return_use_count: int,
) -> dict:
    ids = [vehicle.vehicle_id for vehicle in order]
    obj1 = objective_1(ids, vehicle_by_id)
    obj2 = objective_2(ids, vehicle_by_id)
    obj3 = objective_3(return_use_count)
    obj4 = objective_4(len(order), completion_time)
    scores = {
        "objective_1": obj1["score"],
        "objective_2": obj2["score"],
        "objective_3": obj3["score"],
        "objective_4": obj4["score"],
    }
    weighted = (
        0.4 * scores["objective_1"]
        + 0.3 * scores["objective_2"]
        + 0.2 * scores["objective_3"]
        + 0.1 * scores["objective_4"]
    )
    return {
        "objective_1": obj1,
        "objective_2": obj2,
        "objective_3": obj3,
        "objective_4": obj4,
        "weighted_score": weighted,
    }


def target_order(vehicles: list[Vehicle]) -> list[Vehicle]:
    """Build a deterministic lexicographic target for the weighted objectives.

    The target fills the two non-hybrid slots after each hybrid where possible
    and alternates drive types. It is only a target; PBS feasibility is checked
    by simulation.
    """
    hybrids = [vehicle for vehicle in vehicles if vehicle.power == "\u6df7\u52a8"]
    non_hybrids = [vehicle for vehicle in vehicles if vehicle.power != "\u6df7\u52a8"]
    result: list[Vehicle] = []
    non_index = 0
    for hybrid_index, hybrid in enumerate(hybrids):
        if non_index < len(non_hybrids):
            result.append(non_hybrids[non_index])
            non_index += 1
        if non_index < len(non_hybrids):
            result.append(non_hybrids[non_index])
            non_index += 1
        result.append(hybrid)
    result.extend(non_hybrids[non_index:])
    return result


def improve_by_adjacent_swaps(
    vehicles: list[Vehicle],
    max_passes: int = 2,
    max_swaps: int = 1200,
) -> tuple[list[Vehicle], dict]:
    """Greedily improve the target permutation while keeping it deterministic."""
    current = target_order(vehicles)
    vehicle_by_id = {vehicle.vehicle_id: vehicle for vehicle in vehicles}
    current_score = score_sequence(
        current,
        vehicle_by_id,
        completion_time=9 * len(current) + 72,
        return_use_count=0,
    )["weighted_score"]
    improvements = []
    swaps = 0
    for pass_index in range(max_passes):
        changed = False
        for index in range(len(current) - 1):
            if swaps >= max_swaps:
                break
            candidate = current.copy()
            candidate[index], candidate[index + 1] = candidate[index + 1], candidate[index]
            candidate_score = score_sequence(
                candidate,
                vehicle_by_id,
                completion_time=9 * len(candidate) + 72,
                return_use_count=0,
            )["weighted_score"]
            swaps += 1
            if candidate_score > current_score + 1e-12:
                current = candidate
                current_score = candidate_score
                changed = True
                improvements.append(
                    {
                        "pass": pass_index,
                        "index": index,
                        "score": current_score,
                        "swapped_ids": [current[index + 1].vehicle_id, current[index].vehicle_id],
                    }
                )
        if not changed or swaps >= max_swaps:
            break
    return current, {
        "initial_sequence_score_at_ideal_time": score_sequence(
            target_order(vehicles),
            vehicle_by_id,
            completion_time=9 * len(vehicles) + 72,
            return_use_count=0,
        ),
        "improved_sequence_score_at_ideal_time": score_sequence(
            current,
            vehicle_by_id,
            completion_time=9 * len(current) + 72,
            return_use_count=0,
        ),
        "swaps_evaluated": swaps,
        "improvements": improvements[:200],
    }


def run_target(
    vehicles: list[Vehicle],
    scenario: str,
    strategy: str,
) -> tuple[object, dict]:
    dispatcher = PBSDispatcher(vehicles, scenario=scenario, strategy=strategy)
    result = dispatcher.run()
    return result, detailed_scores(result, dispatcher.vehicle_by_id)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--scenario", choices=("Q1", "Q2"), default="Q1")
    parser.add_argument("--attachment", default="attachment1.xlsx")
    args = parser.parse_args()
    run_root = Path(__file__).resolve().parents[1]
    args.output_root = args.output_root or (run_root / "outputs")
    raw_root = run_root / "inputs-raw"
    source = raw_root / args.attachment
    vehicles = read_vehicles(source)

    start = time.perf_counter()
    improved, search_record = improve_by_adjacent_swaps(vehicles)
    target_result, target_scores = run_target(improved, args.scenario, "greedy")
    runtime = time.perf_counter() - start
    label = f"{args.scenario.lower()}-{args.attachment}-target-greedy"
    result_dir = args.output_root / label
    result_dir.mkdir(parents=True, exist_ok=True)

    write_json(result_dir / "scores.json", target_scores)
    write_json(result_dir / "search-record.json", search_record)
    write_json(
        result_dir / "solver-log.json",
        {
            "benchmark_id": "historical_2022_c_buffer_scheduling",
            "run_id": "run-002",
            "scenario": args.scenario,
            "strategy": "target-sequence + deterministic adjacent-swap heuristic",
            "random_seed": None,
            "time_limit_seconds": None,
            "runtime_seconds": runtime,
            "input_sha256": sha256(source),
            "vehicle_count": len(vehicles),
            "target_weighted_score_at_ideal_time": search_record[
                "improved_sequence_score_at_ideal_time"
            ]["weighted_score"],
            "simulated_score": target_scores["weighted_score"],
            "feasible": target_result.feasible,
            "violations": target_result.violations,
            "completion_time": target_result.completion_time,
            "return_use_count": target_result.return_use_count,
            "termination": "completed" if target_result.feasible else "infeasible",
        },
    )
    write_json(result_dir / "events.json", target_result.event_log)
    export_result_workbook(
        args.output_root / f"candidate-{label}.xlsx",
        target_result,
        len(vehicles),
    )
    print(
        json.dumps(
            {
                "label": label,
                "feasible": target_result.feasible,
                "violations": len(target_result.violations),
                "weighted_score": target_scores["weighted_score"],
                "completion_time": target_result.completion_time,
                "return_use_count": target_result.return_use_count,
                "runtime_seconds": runtime,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
