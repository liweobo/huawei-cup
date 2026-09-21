"""2017F physical failures, declared sensitivities and commissioned-network phasing."""
import csv
import gzip
import json
import math
from collections import defaultdict
import numpy as np
from network_model import RUN,dump,load_inputs,nx


def read_solution():
    d=json.loads((RUN/"results/primary/design.json").read_text(encoding="utf-8"))
    with gzip.open(RUN/"results/primary/routes.json.gz","rt",encoding="utf-8") as f: paths=json.load(f)
    ids,xy,D,locations=load_inputs(); U=D.copy(); np.fill_diagonal(U,0)
    N=len(d["nodes"]); n=d["n_primary"]; M=np.zeros((114,N)); M[:4,:4]=np.eye(4); M[4:,4+n:]=np.array(d["allocation"])
    return d,paths,M.T@U@M,M,U,D,locations


def evaluate(d,paths,B,selected=None,multiplier=1.,source_surge=None,cars=8,acceptance=1.):
    nodes=d["nodes"]; N=len(nodes); idx={v["id"]:i for i,v in enumerate(nodes)}
    pairs={tuple(sorted([idx[e["u"]],idx[e["v"]]])):e for e in d["edges"]}
    built=set(e["id"] for e in d["edges"]) if selected is None else set(selected)
    flow=defaultdict(float); delivered=np.zeros((N,N)); routed=0.
    active_nodes=set(range(4))
    for e in d["edges"]:
        if e["id"] in built: active_nodes.update([idx[e["u"]],idx[e["v"]]])
    for row in paths:
        p=row["path"]; k=row["origin_index"]; dest=row["destination_index"]
        if any(pairs[tuple(sorted([u,v]))]["id"] not in built for u,v in zip(p,p[1:])): continue
        factor=multiplier*(source_surge.get(k,1.) if source_surge else 1.)*acceptance
        amount=row["tonnes_day"]*factor; delivered[k,dest]+=amount; routed+=amount
        for u,v in zip(p,p[1:]): flow[u,v]+=amount
    for i in active_nodes: delivered[i,i]=B[i,i]*multiplier*acceptance
    calls=np.zeros(N); train_equiv=np.zeros(N); length_cost=0.; line_max=0.
    for (u,v),amount in flow.items():
        e=pairs[tuple(sorted([u,v]))]; payload=e["vehicle_tonnes"]*cars
        trains=math.ceil(max(0,amount-1e-7)/payload); calls[u]+=trains; train_equiv[u]+=amount/payload; line_max=max(line_max,trains)
        length_cost+=amount*e["length_km"]
    ground=delivered.sum(0)+delivered.sum(1); ground[:4+d["n_primary"]]=0
    cap_violation=max(0.,float(calls[4:].max()-90)); ground_violation=max(0.,float(ground.max()-3000))
    return {"routed_t_day":routed,"station_local_t_day":float(np.trace(delivered)),"delivered_endpoint_t_day":float(delivered.sum()),
            "station_max_departures":float(calls[4:].max()),"station_violation_departures":cap_violation,"ground_violation_t_day":ground_violation,
            "line_max_departures":line_max,"line_violation_departures":max(0,line_max-540),"underground_tonne_km_day":length_cost,
            "static_capacity_pass":cap_violation==0 and ground_violation<1e-5 and line_max<=540,
            "daily_clearing":"STATIC_ONLY"},delivered,calls,ground


def reachability(d,B,removed):
    nodes=d["nodes"]; idx={n["id"]:i for i,n in enumerate(nodes)}; N=len(nodes)
    g=nx.Graph(); g.add_nodes_from(range(4,N)); park_neighbours=defaultdict(list)
    for e in d["edges"]:
        if e["id"]==removed: continue
        u,v=idx[e["u"]],idx[e["v"]]
        if u<4: park_neighbours[u].append(v)
        elif v<4: park_neighbours[v].append(u)
        else: g.add_edge(u,v)
    comp={n:k for k,nodeset in enumerate(nx.connected_components(g)) for n in nodeset}
    park_components={p:{comp[v] for v in park_neighbours[p]} for p in range(4)}
    reachable=np.eye(N,dtype=bool)
    for i in range(N):
        for j in range(N):
            if i>=4 and j>=4: reachable[i,j]=comp[i]==comp[j]
            elif i<4 and j>=4: reachable[i,j]=comp[j] in park_components[i]
            elif i>=4 and j<4: reachable[i,j]=comp[i] in park_components[j]
    target=B.copy(); np.fill_diagonal(target,0); mask=target>1e-8
    return {"reachable_routed_endpoint_fraction":float((target*reachable).sum()/target.sum()),
            "reachable_positive_endpoint_pair_fraction":float((reachable&mask).sum()/mask.sum()),
            "core_components":nx.number_connected_components(g),"core_isolates":[d["nodes"][i]["id"] for i in nx.isolates(g)]}


def commissioning_order(d):
    nodes=d["nodes"]; idx={n["id"]:i for i,n in enumerate(nodes)}; n=d["n_primary"]; edges=d["edges"]
    first=min((e for e in edges if e["kind"]=="park-primary"),key=lambda e:e["length_km"])
    root=idx[first["v"]] if idx[first["u"]]<4 else idx[first["u"]]
    order=[first]; chosen={first["id"]}; primaries={root}
    feeder={idx[e["u"]]:e for e in edges if e["kind"]=="primary-secondary"}
    order.append(feeder[root]); chosen.add(feeder[root]["id"])
    while len(primaries)<n:
        frontier=[e for e in edges if e["kind"]=="primary-primary" and ((idx[e["u"]] in primaries) != (idx[e["v"]] in primaries))]
        e=min(frontier,key=lambda e:(e["length_km"],e["id"]))
        new=idx[e["v"]] if idx[e["u"]] in primaries else idx[e["u"]]
        order.extend([e,feeder[new]]); chosen.update([e["id"],feeder[new]["id"]]); primaries.add(new)
    order.extend(sorted((e for e in edges if e["id"] not in chosen),key=lambda e:(e["length_km"],e["id"])))
    return order


if __name__=="__main__":
    d,paths,B,M,U,D,locations=read_solution(); base,_,_,_=evaluate(d,paths,B)
    assert base["static_capacity_pass"]
    failures=[]
    for e in d["edges"]:
        r=reachability(d,B,e["id"]); r.update(removed_physical_tunnel=e["id"],kind=e["kind"],both_arcs_removed=True,
                      status="SCENARIO_TOPOLOGICAL_REACHABILITY_NOT_CAPACITY_REROUTING_PROOF")
        failures.append(r)
    dump(RUN/"results/q3-failures.json",{"model":"exhaustive single physical tunnel removal, no probabilities; parks never transit nodes",
      "baseline":base,"scenarios":failures,"count":len(failures),"worst":min(failures,key=lambda r:r["reachable_routed_endpoint_fraction"]),
      "disconnected_scenarios":sum(r["reachable_routed_endpoint_fraction"]<1-1e-9 for r in failures),"global_robustness_claim":False})
    surges=[]
    for x in [1.10,1.25]:
        r,_,_,_=evaluate(d,paths,B,source_surge={0:x}); r.update(scenario=f"park1_outgoing_x{x}",source="ASSUMED_SCENARIO",rerouting="retained paths; overload reported, not admitted as feasible design")
        surges.append(r)
    for cars in [4,8]:
        r,_,_,_=evaluate(d,paths,B,cars=cars); r.update(scenario=f"train_cars_{cars}",source="declared configuration sensitivity within given4-8")
        surges.append(r)
    park_limit={"scenario":"apply_90_departures_to_each_park","maximum_outbound_tonnes_per_park":90*80,
                "source_outbound_tonnes":D[:4].sum(1).tolist(),"interpretation":"Alternative dispatch scope; full park diversion impossible under a park-wide7200t/day bound; not the nominal interpretation"}
    dump(RUN/"results/q3-sensitivity.json",{"scenarios":surges,"park_scope":park_limit})
    geometry=[]
    for offset in [.125,.5]:
        clone=json.loads(json.dumps(d)); old=clone["primary_offset_km"]
        for node in clone["nodes"]:
            if node["type"]=="primary": node["y_km"]+=offset-old
        idx={n["id"]:n for n in clone["nodes"]}
        for e in clone["edges"]:
            a,b=idx[e["u"]],idx[e["v"]]; e["length_km"]=math.hypot(a["x_km"]-b["x_km"],a["y_km"]-b["y_km"])
        r,_,_,_=evaluate(clone,paths,B)
        capital=sum(e["length_km"]*e["price_yuan_per_km"] for e in clone["edges"])
        r.update(offset_km=offset,total_daily_yuan=r["underground_tonne_km_day"]+d["access_tonne_km_day"]+(capital+d["cost"]["station_capital_yuan"])*.01/365,
                 status="LOCATION_SENSITIVITY_ONLY_NOT_ADOPTED; transfer-ratio nearest-association must be rechecked before adoption")
        geometry.append(r)
    smallest=min((node for node in d["nodes"] if node["type"]=="secondary"),key=lambda n:n["ground_exchange_t_day"])
    changes={"position_scenarios":geometry,"node_count_probe":{"remove_secondary":smallest["id"],"unreallocated_exchange_t_day":smallest["ground_exchange_t_day"],"status":"REJECTED_LOST_REQUIRED_SERVICE; no full reallocation search claimed"},
             "node_level_probe":{"candidate":"demote a primary while retaining incident park links","status":"REJECTED_HIERARCHY_VIOLATION; secondary-park links not eligible"},
             "feeder_redundancy_option":{"status":"PROPOSAL_NOT_BUILT_OR_VERIFIED","scope":"Additional independent feeder corridors would target observed bridge failures; same-parent hierarchy and common-cause failures require separate design"}}
    dump(RUN/"results/q3-design-evaluations.json",changes)
    order=commissioning_order(d); total_length=sum(e["length_km"] for e in order); annual=total_length/8
    progress=0.; build=[]
    for e in order:
        start=progress; progress+=e["length_km"]
        build.append({"tunnel":e["id"],"u":e["u"],"v":e["v"],"length_km":e["length_km"],
                      "start_work_km":start,"finish_work_km":progress,"commission_year":min(8,math.ceil((progress-1e-8)/annual)),
                      "annual_work_km":[max(0,min(progress,y*annual)-max(start,(y-1)*annual)) for y in range(1,9)]})
    annual_rows=[]; nodes=d["nodes"]; idx={n["id"]:i for i,n in enumerate(nodes)}
    source_exchange=D.sum(0)+D.sum(1); gamma=np.array([float(r["congestion"]) for r in locations[4:]])
    for y in range(1,9):
        built={b["tunnel"] for b in build if b["commission_year"]<=y}; factor=1.05**y
        raw,_,_,_=evaluate(d,paths,B,selected=built,multiplier=factor)
        lo,hi=0.,1.
        for _ in range(45):
            mid=(lo+hi)/2; test,_,_,_=evaluate(d,paths,B,selected=built,multiplier=factor,acceptance=mid)
            if test["static_capacity_pass"]: lo=mid
            else: hi=mid
        result,served,_,_=evaluate(d,paths,B,selected=built,multiplier=factor,acceptance=lo)
        ratio=np.divide(served,B*factor,out=np.zeros_like(B),where=B>1e-10)
        served_original=U*(M@ratio@M.T)*factor
        surface_endpoint=source_exchange*factor-served_original.sum(0)-served_original.sum(1)
        congestion=gamma*surface_endpoint[4:]/source_exchange[4:]
        g=nx.Graph(); g.add_nodes_from(range(4))
        for e in d["edges"]:
            if e["id"] in built: g.add_edge(idx[e["u"]],idx[e["v"]])
        active_primary=[i for i in g if nodes[i]["type"]=="primary"]
        primary_components=nx.number_connected_components(g.subgraph(active_primary)) if active_primary else 0
        built_station_ids=[nodes[i]["id"] for i in g if i>=4]
        assert primary_components==1
        available=set(range(4))
        for item in build:
            if item["tunnel"] in built: available.update([idx[item["u"]],idx[item["v"]]])
        endpoint_check=all(idx[e["u"]] in available and idx[e["v"]] in available for e in d["edges"] if e["id"] in built)
        source_total=float(D.sum()*factor); remainder=source_total-float(served.sum())
        result.update(year=y,demand_multiplier=factor,annual_work_km=sum(b["annual_work_km"][y-1] for b in build),completed_tunnels=len(built),
          commissioned_stations=built_station_ids,active_primary_components=primary_components,endpoint_dependencies_pass=endpoint_check,
          retained_route_acceptance=lo,unthrottled_station_violation=raw["station_violation_departures"],source_total_t_day=source_total,
          surface_fallback_including_original_diagonal_t_day=remainder,source_accounting_residual=abs(source_total-served.sum()-remainder),
          underground_fraction=float(served.sum()/source_total),regions_above_basic_freeflow=int((congestion>4+1e-8).sum()),max_congestion_index=float(congestion.max()),
          full_target_pass=bool(remainder<=float(np.trace(D))*factor+1e-5 and (congestion<=4+1e-8).all()),
          phase_status="STATIC_FEASIBLE_WITH_SURFACE_FALLBACK_NOT_FULL_TARGET")
        annual_rows.append(result)
    years=[]
    for y in range(31):
        result,_,_,_=evaluate(d,paths,B,multiplier=1.05**y); result.update(year=y,demand_multiplier=1.05**y); years.append(result)
    saturation=next((r["year"] for r in years if not r["static_capacity_pass"]),None)
    last,_,calls,ground=evaluate(d,paths,B,multiplier=1.05**30)
    expansion=[]
    for i,node in enumerate(nodes):
        if node["type"]=="park": continue
        modules=max(1,math.ceil(calls[i]/90),math.ceil(ground[i]/(3000 if node["type"]=="secondary" else 4000)))
        expansion.append({"node":node["id"],"type":node["type"],"parallel_equivalent_station_modules_lower_bound":modules,"additional_modules_lower_bound":modules-1})
    dump(RUN/"results/q4-build-plan.json",{"method":"connected primary-tree/own-feeder commissioning, then remaining links by length; tunnels may span years but incomplete links unavailable",
      "equality_assumption":"segmentable construction work, exactly L/8 each year; no invented tolerance","total_final_length_km":total_length,"annual_target_km":annual,"tunnels":build})
    dump(RUN/"results/q4-annual.json",annual_rows)
    dump(RUN/"results/q4-saturation.json",{"criterion":"first integer year whose unchanged full-demand routing breaches rounded station/line departures or ground exchange","t0":"original full-day OD", "first_saturation_year":saturation,"years":years,
      "thirty_year_status":"SATURATES_BEFORE_30_YEARS" if saturation is not None else "STATIC_CAPACITY_ONLY",
      "expansion":{"status":"CAPACITY_LOWER_BOUND_NOT_A_FEASIBLE_EXPANSION_DESIGN","modules":expansion,"additional_modules_lower_bound":sum(r["additional_modules_lower_bound"] for r in expansion),
                   "warning":"Requires new node locations/corridors, allocations, fleet and operating timetable. Four-track alone does not increase station dispatch. No30-year feasibility claim."}})
    print(json.dumps({"failure_scenarios":len(failures),"failure_worst":min(r["reachable_routed_endpoint_fraction"] for r in failures),"saturation":saturation,
                      "annual":[{k:r[k] for k in ["year","underground_fraction","station_max_departures","regions_above_basic_freeflow"]} for r in annual_rows]},indent=2),flush=True)
