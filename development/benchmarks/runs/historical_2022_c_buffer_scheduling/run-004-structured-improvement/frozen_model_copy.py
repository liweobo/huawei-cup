"""Discrete-event simulation and objective scoring for 2022 C PBS."""

from __future__ import annotations

import json
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from openpyxl import load_workbook


LANE_TRANSFER_TIME = (18, 12, 6, 0, 12, 18)
RETURN_TRANSFER_TIME = (24, 18, 12, 6, 12, 18)
LANE_MOVE_TIME = 9
LANES = 6
POSITIONS = 10

CODE_PAINT_EXIT = 0
CODE_RECEIVE = 1
CODE_DELIVERY = 2
CODE_ASSEMBLY = 3
CODE_RETURN = {position: 70 + position for position in range(1, 11)}
CODE_INBOUND = {
    (lane, position): lane * 100 + position
    for lane in range(1, LANES + 1)
    for position in range(1, POSITIONS + 1)
}


@dataclass
class Vehicle:
    vehicle_id: int
    model: str
    power: str
    drive: str
    source_index: int


@dataclass
class SimulationResult:
    feasible: bool
    violations: list[dict[str, Any]]
    output_order: list[int]
    completion_time: int
    return_use_count: int
    score: float
    objective_scores: dict[str, float]
    timeline: dict[int, dict[int, int | None]]
    event_log: list[dict[str, Any]]
    metrics: dict[str, Any]


@dataclass
class MachineState:
    busy_until: int = 0
    busy_kind: str = "IDLE"
    payload: int | None = None
    destination: tuple[str, int] | None = None


@dataclass
class LaneBody:
    vehicle_id: int
    position: int
    move_started_at: int | None
    move_finishes_at: int | None
    arrival_at_position_1: int | None


class PBSDispatcher:
    """A deterministic, conservative event simulator for the stated PBS rules."""

    def __init__(self, vehicles: list[Vehicle], scenario: str, strategy: str):
        if scenario not in {"Q1", "Q2"}:
            raise ValueError("scenario must be Q1 or Q2")
        if strategy not in {"source-order", "greedy"}:
            raise ValueError("strategy must be source-order or greedy")
        self.vehicles = vehicles
        self.vehicle_by_id = {vehicle.vehicle_id: vehicle for vehicle in vehicles}
        self.scenario = scenario
        self.strategy = strategy
        self.inbound: dict[int, deque[LaneBody]] = {
            lane: deque() for lane in range(1, LANES + 1)
        }
        # Each deque is sorted by increasing position. Position 1 is the
        # delivery point; newly received vehicles are appended at position 10.
        self.return_lane: deque[LaneBody] = deque()
        self.receive = MachineState()
        self.delivery = MachineState()
        self.pending_receive: dict[str, Any] | None = None
        self.time = 0
        self.next_source = 0
        self.output_order: list[int] = []
        self.return_use_count = 0
        self.event_log: list[dict[str, Any]] = []
        self.timeline: dict[int, dict[int, int | None]] = {
            vehicle.vehicle_id: {} for vehicle in vehicles
        }
        self.violations: list[dict[str, Any]] = []
        self.max_time = max(20000, 200 * len(vehicles))
        self._record_initial_state()

    @property
    def done(self) -> bool:
        return self.next_source >= len(self.vehicles) and not self.return_lane and all(
            not lane for lane in self.inbound.values()
        )

    def _record_initial_state(self) -> None:
        for vehicle in self.vehicles:
            self.timeline[vehicle.vehicle_id][0] = CODE_PAINT_EXIT

    def _vehicle_at(self, location: tuple[str, int]) -> int | None:
        kind, index = location
        if kind == "inbound":
            lane = self.inbound[index]
            return lane[0].vehicle_id if lane else None
        if kind == "return":
            return (
                max(self.return_lane, key=lambda body: body.position).vehicle_id
                if self.return_lane
                else None
            )
        raise ValueError(location)

    @staticmethod
    def _ordered_lane(lane: deque[LaneBody]) -> list[LaneBody]:
        return sorted(lane, key=lambda body: body.position)

    def _lane_body_at(self, lane_number: int, position: int) -> LaneBody | None:
        for body in self.inbound[lane_number]:
            if body.position == position:
                return body
        return None

    def _record(self, time: int, vehicle_id: int, code: int) -> None:
        self.timeline.setdefault(vehicle_id, {})[time] = code

    def _advance_lane_movements(self) -> None:
        """Advance all eligible FIFO movements at one nine-second epoch."""
        # Process from position 9 down to 1 so a vacated slot can be reused.
        for lane_number, lane in enumerate(self.inbound.values(), 1):
            occupied = {body.position: body for body in self._ordered_lane(lane)}
            for position in range(2, POSITIONS + 1):
                body = occupied.get(position)
                if (
                    body is None
                    or body.move_finishes_at is None
                    or body.move_finishes_at > self.time
                ):
                    continue
                if position - 1 in occupied:
                    continue
                body.position -= 1
                occupied.pop(position, None)
                occupied[position - 1] = body
                body.move_started_at = None
                body.move_finishes_at = None
                if body.position == 1:
                    body.arrival_at_position_1 = self.time
                self._record(
                    self.time,
                    body.vehicle_id,
                    CODE_INBOUND[(lane_number, body.position)],
                )
                self.event_log.append(
                    {
                        "time": self.time,
                        "event": "lane_move_complete",
                        "lane": lane_number,
                        "from_position": position,
                        "to_position": body.position,
                        "vehicle_id": body.vehicle_id,
                    }
                )
            self._rebuild_lane(lane, occupied)

        occupied_return = {body.position: body for body in self._ordered_lane(self.return_lane)}
        for position in range(1, POSITIONS):
            body = occupied_return.get(position)
            if (
                body is None
                or body.move_finishes_at is None
                or body.move_finishes_at > self.time
            ):
                continue
            if position + 1 in occupied_return:
                continue
            body.position += 1
            occupied_return.pop(position, None)
            occupied_return[position + 1] = body
            body.move_started_at = None
            body.move_finishes_at = None
            self._record(
                self.time,
                body.vehicle_id,
                CODE_RETURN[body.position],
            )
            self.event_log.append(
                {
                    "time": self.time,
                    "event": "return_move_complete",
                    "from_position": position,
                    "to_position": body.position,
                    "vehicle_id": body.vehicle_id,
                }
            )
        self._rebuild_return(occupied_return)

    def _rebuild_lane(self, lane: deque[LaneBody], occupied: dict[int, LaneBody]) -> None:
        lane.clear()
        for position in range(1, POSITIONS + 1):
            body = occupied.get(position)
            if body is not None:
                lane.append(body)

    def _rebuild_return(self, occupied: dict[int, LaneBody]) -> None:
        self.return_lane.clear()
        for position in range(1, POSITIONS + 1):
            body = occupied.get(position)
            if body is not None:
                self.return_lane.append(body)

    def _schedule_downstream_moves(self) -> None:
        # A body at p can start when p+1 is empty; the event completes after 9s.
        for lane_number, lane in enumerate(self.inbound.values(), 1):
            occupied = {body.position: body for body in self._ordered_lane(lane)}
            for position in range(2, POSITIONS + 1):
                body = occupied.get(position)
                if body is None or body.move_started_at is not None:
                    continue
                if position - 1 in occupied:
                    continue
                body.move_started_at = self.time
                body.move_finishes_at = self.time + LANE_MOVE_TIME
                self.event_log.append(
                    {
                        "time": self.time,
                        "event": "lane_move_started",
                        "lane": lane_number,
                        "from_position": position,
                        "vehicle_id": body.vehicle_id,
                    }
                )
            self._rebuild_lane(lane, occupied)
        occupied_return = {body.position: body for body in self._ordered_lane(self.return_lane)}
        for position in range(1, POSITIONS):
            body = occupied_return.get(position)
            if body is None or body.move_started_at is not None:
                continue
            if position + 1 in occupied_return:
                continue
            body.move_started_at = self.time
            body.move_finishes_at = self.time + LANE_MOVE_TIME
        self._rebuild_return(occupied_return)

    def _can_receive(self) -> bool:
        return self.receive.busy_until <= self.time and self.next_source < len(
            self.vehicles
        )

    def _can_deliver(self) -> bool:
        return self.delivery.busy_until <= self.time

    def _choose_receive_destination(self, vehicle: Vehicle) -> int | None:
        if self.strategy == "source-order":
            candidates = [
                lane_number
                for lane_number, lane in self.inbound.items()
                if len(lane) < POSITIONS
                and self._lane_body_at(lane_number, POSITIONS) is None
            ]
            if not candidates:
                return None
            # Spread bodies across lanes to avoid one lane becoming unavailable.
            return min(candidates, key=lambda lane_number: (len(self.inbound[lane_number]), lane_number))

        # Greedy: try to put downstream-compatible bodies where they are useful.
        candidates = [
            lane_number
            for lane_number, lane in self.inbound.items()
            if len(lane) < POSITIONS
            and self._lane_body_at(lane_number, POSITIONS) is None
        ]
        if not candidates:
            return None
        # Favor an earlier expected output for power/drive runs, while retaining
        # capacity balance as the tie breaker.
        desired = 0 if vehicle.drive == "\u56db\u9a71" else 1
        return min(
            candidates,
            key=lambda lane_number: (
                abs((lane_number % 2) - desired),
                len(self.inbound[lane_number]),
                lane_number,
            ),
        )

    def _start_receive(self, vehicle: Vehicle, destination: int) -> None:
        if self._lane_body_at(destination, POSITIONS) is not None:
            self.violations.append(
                {
                    "time": self.time,
                    "rule": "receive_destination_occupied",
                    "message": f"lane {destination} position 10 occupied",
                }
            )
        duration = LANE_TRANSFER_TIME[destination - 1]
        self.receive.busy_until = self.time + duration
        self.receive.busy_kind = "PAINT_TO_LANE"
        self.receive.payload = vehicle.vehicle_id
        self.receive.destination = ("inbound", destination)
        self._record(self.time, vehicle.vehicle_id, CODE_RECEIVE)
        self._record(
            self.time + duration,
            vehicle.vehicle_id,
            CODE_INBOUND[(destination, POSITIONS)],
        )
        self.pending_receive = {
            "vehicle_id": vehicle.vehicle_id,
            "destination": destination,
            "finish_time": self.time + duration,
        }
        self.next_source += 1
        self.event_log.append(
            {
                "time": self.time,
                "event": "receive_paint_start",
                "vehicle_id": vehicle.vehicle_id,
                "lane": destination,
                "duration": duration,
            }
        )

    def _lane_position_one_candidate(self) -> tuple[int, int] | None:
        candidates = [
            (
                lane_number,
                self._lane_body_at(lane_number, 1).vehicle_id,
                self._lane_body_at(lane_number, 1).arrival_at_position_1,
            )
            for lane_number, lane in self.inbound.items()
            if self._lane_body_at(lane_number, 1) is not None
        ]
        if not candidates:
            return None
        if self.scenario == "Q1":
            return min(candidates, key=lambda item: (item[2] is None, item[2], item[0]))[:2]
        return min(candidates, key=lambda item: item[0])[:2]

    def _return_position_ten_candidate(self) -> int | None:
        if not self.return_lane:
            return None
        body = self._ordered_lane(self.return_lane)[-1]
        return body.vehicle_id if body.position == POSITIONS else None

    def _choose_delivery_action(self) -> tuple[str, int, int] | None:
        lane_candidate = self._lane_position_one_candidate()
        return_candidate = self._return_position_ten_candidate()
        receive_available = (
            self.scenario == "Q1"
            and self._can_receive()
            and return_candidate is not None
        )

        # Return position 10 has priority in Q1. In Q2 the priority is removed,
        # but the return lane can only be consumed by the receiving machine.
        if receive_available:
            return ("return_to_lane", 0, return_candidate)
        if self._can_deliver() and lane_candidate is not None:
            lane, vehicle_id = lane_candidate
            # Q1/Q2 both prefer final assembly unless the body is needed to
            # create a targeted output pattern and the return lane can be used.
            use_return = self._should_return(vehicle_id, lane)
            if use_return and receive_available:
                return ("to_return", lane, vehicle_id)
            if self._can_deliver():
                return ("to_assembly", lane, vehicle_id)
        return None

    def _should_return(self, vehicle_id: int, lane: int) -> bool:
        if self.strategy == "source-order":
            return False
        vehicle = self.vehicle_by_id[vehicle_id]
        recent = [self.vehicle_by_id[v] for v in self.output_order[-3:]]
        hybrid_recent = sum(item.power == "\u6df7\u52a8" for item in recent)
        if vehicle.power == "\u6df7\u52a8" and hybrid_recent >= 2:
            return True
        drive_counts = {
            "\u4e24\u9a71": sum(item.drive == "\u4e24\u9a71" for item in recent),
            "\u56db\u9a71": sum(item.drive == "\u56db\u9a71" for item in recent),
        }
        if vehicle.drive == "\u56db\u9a71" and drive_counts["\u56db\u9a71"] > drive_counts["\u4e24\u9a71"]:
            return True
        return False

    def _start_return_to_lane(self, vehicle_id: int) -> None:
        if not self.return_lane:
            self.violations.append(
                {"time": self.time, "rule": "return_position_10", "message": "empty return lane"}
            )
            return
        body = max(self.return_lane, key=lambda item: item.position)
        self.return_lane.remove(body)
        if body.position != POSITIONS:
            self.violations.append(
                {
                    "time": self.time,
                    "rule": "return_position_10",
                    "message": "return body not at position 10",
                }
            )
        destination = self._choose_receive_destination(self.vehicle_by_id[vehicle_id])
        duration = RETURN_TRANSFER_TIME[destination - 1]
        self.receive.busy_until = self.time + duration
        self.receive.busy_kind = "RETURN_TO_LANE"
        self.receive.payload = vehicle_id
        self.receive.destination = ("inbound", destination)
        self._record(self.time, vehicle_id, CODE_RECEIVE)
        self._record(
            self.time + duration,
            vehicle_id,
            CODE_INBOUND[(destination, POSITIONS)],
        )
        self.pending_receive = {
            "vehicle_id": vehicle_id,
            "destination": destination,
            "finish_time": self.time + duration,
        }
        self.event_log.append(
            {
                "time": self.time,
                "event": "receive_return_start",
                "vehicle_id": vehicle_id,
                "lane": destination,
                "duration": duration,
            }
        )

    def _start_assembly(self, lane: int, vehicle_id: int) -> None:
        duration = LANE_TRANSFER_TIME[lane - 1]
        self.delivery.busy_until = self.time + duration
        self.delivery.busy_kind = "LANE_TO_ASSEMBLY"
        self.delivery.payload = vehicle_id
        self.delivery.destination = ("assembly", 0)
        self._record(self.time, vehicle_id, CODE_DELIVERY)
        self._record(self.time + duration, vehicle_id, CODE_ASSEMBLY)
        body = self._lane_body_at(lane, 1)
        if body is None or body.vehicle_id != vehicle_id:
            self.violations.append(
                {
                    "time": self.time,
                    "rule": "delivery_lane_position_1",
                    "message": "delivery did not remove position 1 body",
                }
            )
        else:
            self.inbound[lane].remove(body)
        self.output_order.append(vehicle_id)
        self.event_log.append(
            {
                "time": self.time,
                "event": "delivery_assembly_start",
                "vehicle_id": vehicle_id,
                "lane": lane,
                "duration": duration,
            }
        )

    def _start_return(self, lane: int, vehicle_id: int) -> None:
        duration = RETURN_TRANSFER_TIME[lane - 1]
        self.delivery.busy_until = self.time + duration
        self.delivery.busy_kind = "LANE_TO_RETURN"
        self.delivery.payload = vehicle_id
        self.delivery.destination = ("return", 1)
        self._record(self.time, vehicle_id, CODE_DELIVERY)
        self._record(self.time + duration, vehicle_id, CODE_RETURN[1])
        body = self._lane_body_at(lane, 1)
        if body is None or body.vehicle_id != vehicle_id:
            self.violations.append(
                {
                    "time": self.time,
                    "rule": "return_lane_position_1",
                    "message": "return transfer did not remove position 1 body",
                }
            )
        else:
            self.inbound[lane].remove(body)
        self.return_lane.append(LaneBody(vehicle_id, 1, None, None, None))
        self.return_use_count += 1
        self.event_log.append(
            {
                "time": self.time,
                "event": "delivery_return_start",
                "vehicle_id": vehicle_id,
                "lane": lane,
                "duration": duration,
            }
        )

    def _record_idle_violation(self) -> None:
        occupied = [
            lane_number
            for lane_number, lane in self.inbound.items()
            if self._lane_body_at(lane_number, 1) is not None
        ]
        if occupied and self.delivery.busy_until <= self.time:
            self.violations.append(
                {
                    "time": self.time,
                    "rule": "delivery_not_idle_with_position_one",
                    "message": f"occupied lanes: {occupied}",
                }
            )

    def run(self) -> SimulationResult:
        while not self.done and self.time <= self.max_time:
            if (
                self.pending_receive is not None
                and self.pending_receive["finish_time"] <= self.time
            ):
                pending = self.pending_receive
                self.pending_receive = None
                destination = pending["destination"]
                self.inbound[destination].append(
                    LaneBody(
                        vehicle_id=pending["vehicle_id"],
                        position=POSITIONS,
                        move_started_at=None,
                        move_finishes_at=None,
                        arrival_at_position_1=None,
                    )
                )
            # Lane movement completion is checked every second; new movement
            # starts are still aligned to the stated 9-second duration.
            self._advance_lane_movements()
            if self.time % LANE_MOVE_TIME == 0:
                self._schedule_downstream_moves()

            actions_this_second = 0
            while True:
                action = self._choose_delivery_action()
                if action is None:
                    break
                kind, lane, vehicle_id = action
                if kind == "return_to_lane":
                    self._start_return_to_lane(vehicle_id)
                elif kind == "to_assembly":
                    self._start_assembly(lane, vehicle_id)
                elif kind == "to_return":
                    self._start_return(lane, vehicle_id)
                else:
                    self.violations.append(
                        {
                            "time": self.time,
                            "rule": "unknown_action",
                            "message": kind,
                        }
                    )
                actions_this_second += 1
                if actions_this_second > len(self.vehicles) + 10:
                    self.violations.append(
                        {
                            "time": self.time,
                            "rule": "action_loop",
                            "message": "too many zero-duration actions",
                        }
                    )
                    break
            if actions_this_second == 0:
                self._record_idle_violation()

            if self._can_receive() and self.next_source < len(self.vehicles):
                vehicle = self.vehicles[self.next_source]
                destination = self._choose_receive_destination(vehicle)
                if destination is not None:
                    self._start_receive(vehicle, destination)
            self.time += 1

        if self.done:
            completion_time = max(
                (max(values) for values in self.timeline.values() if values),
                default=0,
            )
        else:
            completion_time = self.max_time
            self.violations.append(
                {
                    "time": self.time,
                    "rule": "completion",
                    "message": "simulation did not complete",
                }
            )
        self._fill_timeline_gaps(completion_time)
        objective_scores = score_schedule(
            self.output_order, self.return_use_count, len(self.vehicles), completion_time
        )
        score = weighted_score(objective_scores)
        metrics = self._compute_metrics()
        return SimulationResult(
            feasible=not self.violations,
            violations=self.violations,
            output_order=self.output_order,
            completion_time=completion_time,
            return_use_count=self.return_use_count,
            score=score,
            objective_scores=objective_scores,
            timeline=self.timeline,
            event_log=self.event_log,
            metrics=metrics,
        )

    def _fill_timeline_gaps(self, completion_time: int) -> None:
        for vehicle_id, timeline in self.timeline.items():
            for time in range(1, completion_time + 1):
                if time not in timeline:
                    timeline[time] = None

    def _compute_metrics(self) -> dict[str, Any]:
        lane_occupancy = {lane: len(queue) for lane, queue in self.inbound.items()}
        return {
            "input_vehicles": len(self.vehicles),
            "output_vehicles": len(self.output_order),
            "return_lane_use_count": self.return_use_count,
            "final_lane_occupancy": lane_occupancy,
            "return_lane_occupancy": len(self.return_lane),
            "receive_busy_until": self.receive.busy_until,
            "delivery_busy_until": self.delivery.busy_until,
        }


def read_vehicles(path: Path) -> list[Vehicle]:
    workbook = load_workbook(path, read_only=True, data_only=True)
    worksheet = workbook.worksheets[0]
    rows = list(worksheet.iter_rows(values_only=True))
    workbook.close()
    vehicles: list[Vehicle] = []
    for index, row in enumerate(rows[1:], 1):
        if row[0] is None:
            continue
        vehicles.append(
            Vehicle(
                vehicle_id=int(row[0]),
                model=str(row[1]),
                power=str(row[2]),
                drive=str(row[3]),
                source_index=index,
            )
        )
    return vehicles


def objective_1(order: list[int], vehicles: dict[int, Vehicle]) -> dict[str, Any]:
    positions = [
        index for index, vehicle_id in enumerate(order) if vehicles[vehicle_id].power == "\u6df7\u52a8"
    ]
    deductions = 0
    gaps: list[int] = []
    for left, right in zip(positions, positions[1:]):
        gap = order[left + 1 : right]
        gaps.append(len(gap))
        if len(gap) != 2:
            deductions += 1
    return {
        "score": max(0.0, 100.0 - deductions),
        "hybrid_count": len(positions),
        "pair_gaps": gaps,
        "deductions": deductions,
    }


def _partition_drive_sequence(sequence: list[str]) -> list[list[str]]:
    if not sequence:
        return []
    blocks: list[list[str]] = []
    current = [sequence[0]]
    if sequence[0] == "\u56db\u9a71":
        switch_from, switch_to = "\u4e24\u9a71", "\u56db\u9a71"
    else:
        switch_from, switch_to = "\u56db\u9a71", "\u4e24\u9a71"
    for previous, current_value in zip(sequence, sequence[1:]):
        if previous == switch_from and current_value == switch_to:
            blocks.append(current)
            current = [current_value]
        else:
            current.append(current_value)
    blocks.append(current)
    return blocks


def objective_2(order: list[int], vehicles: dict[int, Vehicle]) -> dict[str, Any]:
    sequence = [vehicles[vehicle_id].drive for vehicle_id in order]
    blocks = _partition_drive_sequence(sequence)
    bad_blocks = []
    for index, block in enumerate(blocks):
        four = sum(value == "\u56db\u9a71" for value in block)
        two = sum(value == "\u4e24\u9a71" for value in block)
        if four == 0 or two == 0 or four != two:
            bad_blocks.append({"index": index, "four": four, "two": two, "length": len(block)})
    return {
        "score": max(0.0, 100.0 - len(bad_blocks)),
        "block_count": len(blocks),
        "bad_blocks": bad_blocks,
    }


def objective_3(return_use_count: int) -> dict[str, Any]:
    return {
        "score": max(0.0, 100.0 - return_use_count),
        "return_use_count": return_use_count,
    }


def objective_4(vehicle_count: int, completion_time: int) -> dict[str, Any]:
    ideal = 9 * vehicle_count + 72
    penalty = 0.01 * max(0, completion_time - ideal)
    return {
        "score": max(0.0, 100.0 - penalty),
        "ideal_time": ideal,
        "completion_time": completion_time,
        "time_penalty": penalty,
    }


def score_schedule(
    order: list[int],
    return_use_count: int,
    vehicle_count: int,
    completion_time: int,
) -> dict[str, float]:
    # The caller supplies the original vehicles only through the returned
    # objective details below; this compact score function is kept for the
    # simulator's internal use.
    # `objective_1` and `objective_2` require attributes, so use a neutral
    # fallback only when an order is incomplete.
    if not order:
        return {"objective_1": 0.0, "objective_2": 0.0, "objective_3": 100.0, "objective_4": 100.0}
    return {"objective_1": 0.0, "objective_2": 0.0, "objective_3": float(max(0, 100 - return_use_count)), "objective_4": float(max(0, 100 - 0.01 * max(0, completion_time - (9 * vehicle_count + 72))))}


def weighted_score(scores: dict[str, float]) -> float:
    return (
        0.4 * scores["objective_1"]
        + 0.3 * scores["objective_2"]
        + 0.2 * scores["objective_3"]
        + 0.1 * scores["objective_4"]
    )


def detailed_scores(
    result: SimulationResult, vehicles: dict[int, Vehicle]
) -> dict[str, Any]:
    obj1 = objective_1(result.output_order, vehicles)
    obj2 = objective_2(result.output_order, vehicles)
    obj3 = objective_3(result.return_use_count)
    obj4 = objective_4(len(vehicles), result.completion_time)
    scores = {
        "objective_1": obj1["score"],
        "objective_2": obj2["score"],
        "objective_3": obj3["score"],
        "objective_4": obj4["score"],
    }
    return {
        "objective_1": obj1,
        "objective_2": obj2,
        "objective_3": obj3,
        "objective_4": obj4,
        "weighted_score": weighted_score(scores),
    }


def export_result_workbook(
    path: Path,
    result: SimulationResult,
    vehicle_count: int,
) -> None:
    from openpyxl import Workbook

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Sheet1"
    worksheet.cell(row=1, column=1, value=None)
    for second in range(result.completion_time + 1):
        worksheet.cell(row=1, column=second + 2, value=second)
    for row_index, vehicle_id in enumerate(range(1, vehicle_count + 1), start=2):
        worksheet.cell(row=row_index, column=1, value=vehicle_id)
        timeline = result.timeline.get(vehicle_id, {})
        for second in range(result.completion_time + 1):
            code = timeline.get(second)
            if code is not None:
                worksheet.cell(row=row_index, column=second + 2, value=code)
    workbook.save(path)


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
