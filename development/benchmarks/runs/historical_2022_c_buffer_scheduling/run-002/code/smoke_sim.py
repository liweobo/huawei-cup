"""Small synthetic smoke test for the PBS event simulator."""

from __future__ import annotations

from pbs_model import PBSDispatcher, Vehicle, detailed_scores


def main() -> None:
    vehicles = [
        Vehicle(1, "A", "\u6df7\u52a8", "\u56db\u9a71", 1),
        Vehicle(2, "B", "\u71c3\u6cb9", "\u4e24\u9a71", 2),
        Vehicle(3, "A", "\u6df7\u52a8", "\u4e24\u9a71", 3),
        Vehicle(4, "B", "\u71c3\u6cb9", "\u56db\u9a71", 4),
        Vehicle(5, "A", "\u6df7\u52a8", "\u4e24\u9a71", 5),
        Vehicle(6, "B", "\u71c3\u6cb9", "\u56db\u9a71", 6),
    ]
    dispatcher = PBSDispatcher(vehicles, scenario="Q1", strategy="source-order")
    result = dispatcher.run()
    print("feasible", result.feasible)
    print("violations", result.violations)
    print("output", result.output_order)
    print("completion", result.completion_time, "returns", result.return_use_count)
    print("scores", detailed_scores(result, dispatcher.vehicle_by_id))
    for event in result.event_log:
        print(event)
    for vehicle_id, timeline in result.timeline.items():
        nonconstant = {
            time: code
            for time, code in timeline.items()
            if code != timeline.get(0)
        }
        print("timeline", vehicle_id, "changes", len(nonconstant), "last", max(nonconstant, default=0))


if __name__ == "__main__":
    main()
