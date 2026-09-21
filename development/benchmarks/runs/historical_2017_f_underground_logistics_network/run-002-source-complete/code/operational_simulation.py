"""Bounded, deterministic queue-policy experiment on this run's saved routes."""
import csv
import gzip
import heapq
import json
import sys
from collections import defaultdict, deque
from pathlib import Path

RUN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN.parents[4] / "skill/scripts"))
from stateful_scheduling import validate_stateful_contract, legal_action_errors
from mechanism_closure import assess_contract


def dump(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def contracts():
    stateful = dict(problem_type="STATEFUL_SCHEDULING",
        state_variables=["clock", "ready freight by route leg", "pending arrivals", "delivered mass"],
        resources=["one station departure per 12 minutes", "park directional arc departure per 2 minutes", "8-car payload"],
        queues_or_buffers=["unlimited freight queues; unlimited available trains assumed"],
        time_representation="event time in minutes; arrivals before departures at equal times",
        terminal_condition="stop at 1080 minutes; unfinished mass is not discarded",
        legal_action_definition="dispatch only ready freight on its next saved arc within payload and fixed resource slot",
        transition_definition="remove FIFO freight, enqueue arrival at length/0.81 km/min; transfer delay 0 or12 minutes",
        hard_invariants=["nonnegative mass", "route precedence", "payload", "headway", "dispatch slots", "mass balance"],
        objective_definition="delivered tonnes by1080; no static-cost optimum or timetable optimality claim",
        candidate_representation="STATE_COUPLED", search_mode="two declared deterministic scenarios, no optimized timetable",
        decoder_required=False, feasibility_mode="BY_CONSTRUCTION", status="PASS")
    closure = dict(model_name="2017F queue-policy scenarios", prediction_or_simulation_target="18-hour delivery",
        closure_scope="declared saved routes, unlimited trains/queues; not calibrated actual operations",
        identifiability_status="LIMITED", numerical_termination_verified=True,
        assumptions_added=[], model_form_uncertainty={"status":"PRESENT", "acknowledged":True})
    specs = [
        ("geometry_requirements", "route_geometry", "DERIVED", "saved primary design/route coordinates", "saved arc lengths", "km"),
        ("state_initial_requirements", "initial_release", "ASSUMED", "A12", "all routed freight ready at t=0", "tonne"),
        ("boundary_interface_requirements", "fleet_buffer", "ASSUMED", "operating scenario", "unlimited trains, no empty return constraint, unlimited queues", "trains"),
        ("boundary_interface_requirements", "handling", "ASSUMED", "sensitivity, not inferred from hourly dispatch", [0,12], "minutes per transfer"),
        ("forcing_input_requirements", "demand", "DERIVED", "original directed OD via saved allocation/routes", "saved route masses", "tonne/day"),
        ("material_constitutive_requirements", "speed", "GIVEN", "DOC appendix", 13.5, "m/s"),
        ("material_constitutive_requirements", "kinematics", "ASSUMED", "A15", "constant speed; no acceleration/deceleration or switch movement", "model form"),
        ("termination_horizon_requirements", "horizon", "GIVEN", "DOC appendix", 1080, "minutes"),
    ]
    for category,name,kind,source,value,unit in specs:
        req=dict(name=name,meaning=name,required_for="queue simulation",source_type=kind,source=source,
                 value_or_parameter=value,unit=unit,status="ASSUMED" if kind=="ASSUMED" else "RESOLVED",
                 essential=True,assumption_reason="scenario closure, not source fact" if kind=="ASSUMED" else "")
        closure.setdefault(category,[]).append(req)
        if kind=="ASSUMED":
            closure["assumptions_added"].append(dict(name=name,reason=req["assumption_reason"],
                plausible_range=str(value),result_dependency="delivery conditional on this simplifying scenario"))
    statecheck=validate_stateful_contract(stateful)
    mechcheck=assess_contract(closure,"SCENARIO_RESULT")
    assert statecheck["status"]=="PASS" and mechcheck["claim_allowed"] and not mechcheck["reviewer_codes"]
    dump(RUN/"operation-contract.json",dict(stateful=stateful,mechanism_closure=closure,stateful_check=statecheck,closure_check=mechcheck))


def simulate(design, routes, handling):
    nodes=design["nodes"]; index={n["id"]:i for i,n in enumerate(nodes)}
    edges={}; outgoing=defaultdict(list)
    for e in design["edges"]:
        u,v=index[e["u"]],index[e["v"]]
        for a,b in [(u,v),(v,u)]:
            edges[a,b]=e; outgoing[a].append((a,b))
    queues=defaultdict(deque); ready=defaultdict(float); events=[]; serial=0
    def event(t,kind,data):
        nonlocal serial
        serial+=1; heapq.heappush(events,(t,kind,serial,data))
    def enqueue(rid,step,amount):
        p=routes[rid]["path"]; arc=(p[step],p[step+1])
        queues[arc].append([rid,step,amount]); ready[arc]+=amount
    for rid,r in enumerate(routes): enqueue(rid,0,r["tonnes_day"])
    for u in range(4,len(nodes)):
        for t in range(0,1080,12): event(t,2,(u,None))
    for u in range(4):
        for arc in outgoing[u]:
            for t in range(0,1080,2): event(t,2,(u,arc))
    initial=sum(r["tonnes_day"] for r in routes)
    delivered=0.; pending=0.; time_weight=0.; trips=0; departure_count=defaultdict(int)
    folder=RUN/"results"/f"operation-handling-{handling}"; folder.mkdir(exist_ok=True)
    with gzip.open(folder/"legs.csv.gz","wt",encoding="utf-8",newline="") as f:
        writer=csv.writer(f); writer.writerow(["train","route_id","step","u","v","depart_min","arrival_min","ready_next_min","tonnes"])
        while events and events[0][0]<=1080:
            t,kind,_,data=heapq.heappop(events)
            if kind==0:
                rid,step,amount=data; pending-=amount
                if step==len(routes[rid]["path"])-2:
                    delivered+=amount; time_weight+=amount*t
                else:
                    pending+=amount; event(t+handling,1,(rid,step+1,amount))
                continue
            if kind==1:
                rid,step,amount=data; pending-=amount; enqueue(rid,step,amount); continue
            u,fixed=data
            legal=[a for a in ([fixed] if fixed is not None else outgoing[u]) if ready[a]>1e-7]
            if not legal: continue
            arc=max(legal,key=lambda a:(ready[a]/(edges[a]["vehicle_tonnes"]*8),-a[1]))
            assert not legal_action_errors(ready,arc,legal_actions=lambda _:legal)
            capacity=edges[arc]["vehicle_tonnes"]*8; remaining=capacity
            trips+=1; departure_count[u]+=1
            while queues[arc] and remaining>1e-8:
                rid,step,amount=queues[arc][0]; take=min(amount,remaining)
                arrival=t+edges[arc]["length_km"]/.81
                writer.writerow([trips,rid,step,*arc,t,format(arrival,".12g"),format(arrival+handling,".12g"),format(take,".15g")])
                event(arrival,0,(rid,step,take)); pending+=take
                remaining-=take; ready[arc]-=take; queues[arc][0][2]-=take
                if queues[arc][0][2]<1e-8: queues[arc].popleft()
            assert remaining>=-1e-8 and ready[arc]>=-1e-6
    queued=sum(ready.values()); residual=abs(initial-delivered-pending-queued)
    assert residual<1e-5
    result=dict(policy="largest ready train-equivalent arc, FIFO within arc; fixed departure slots",
        handling_min=handling,horizon_min=1080,initial_routed_t=initial,delivered_t=delivered,
        queued_t=queued,in_transit_or_handling_t=pending,mass_residual_t=residual,
        delivered_fraction=delivered/initial,mean_delivery_time_delivered_min=time_weight/delivered,
        train_departures=trips,max_station_departures=max(departure_count[i] for i in range(4,len(nodes))),
        station_local_t=design["station_local_t_day"],original_diagonal_surface_t=design["original_diagonal_surface_t_day"],
        daily_clearing="FULL_UNDER_SCENARIO" if pending+queued<1e-5 else "FAILED_POLICY_NOT_INFEASIBILITY_PROOF",
        scope="routed freight only; station-local freight is separately accounted without underground train movement")
    dump(folder/"summary.json",result); return result


if __name__=="__main__":
    contracts()
    design=json.loads((RUN/"results/primary/design.json").read_text(encoding="utf-8"))
    with gzip.open(RUN/"results/primary/routes.json.gz","rt",encoding="utf-8") as f: routes=json.load(f)
    rows=[simulate(design,routes,h) for h in [0,12]]
    dump(RUN/"results/q3-operations.json",rows)
    print(json.dumps(rows,indent=2))
