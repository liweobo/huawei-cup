"""Independent replay of saved legs and phase plans; no modeling helpers imported."""
import csv
import gzip
import json
import math
from collections import defaultdict
from pathlib import Path
import numpy as np

RUN=Path(__file__).resolve().parents[1]


def read(name):
    return json.loads((RUN/name).read_text(encoding="utf-8"))


def operation_audit(d,routes,handling):
    edges={}
    idx={n["id"]:i for i,n in enumerate(d["nodes"])}
    for e in d["edges"]:
        u,v=idx[e["u"]],idx[e["v"]]
        edges[u,v]=edges[v,u]=e
    schedules=defaultdict(list); arrivals=defaultdict(list); amounts=defaultdict(float); trains={}
    with gzip.open(RUN/f"results/operation-handling-{handling}/legs.csv.gz","rt",encoding="utf-8") as f:
        for row in csv.DictReader(f):
            train,rid,step,u,v=[int(row[k]) for k in ["train","route_id","step","u","v"]]
            dep,arr,ready,mass=[float(row[k]) for k in ["depart_min","arrival_min","ready_next_min","tonnes"]]
            assert routes[rid]["path"][step:step+2]==[u,v]
            assert 0<=dep<1080 and mass>0
            assert abs(arr-dep-edges[u,v]["length_km"]/.81)<1e-7
            assert abs(ready-arr-handling)<1e-7
            if train not in trains: trains[train]=[u,v,dep,0.]
            assert trains[train][:3]==[u,v,dep]
            trains[train][3]+=mass
            schedules[rid,step].append((dep,1,-mass))
            amounts[rid,step]+=mass
            if step+1<len(routes[rid]["path"])-1: schedules[rid,step+1].append((ready,0,mass))
            arrivals[rid,step].append((arr,mass))
    station=defaultdict(list); arcs=defaultdict(list)
    for u,v,t,mass in trains.values():
        assert mass<=edges[u,v]["vehicle_tonnes"]*8+1e-7
        arcs[u,v].append(t)
        if u>=4: station[u].append(t)
    for times in station.values():
        times.sort(); assert len(times)<=90 and all(b-a>=12-1e-8 for a,b in zip(times,times[1:]))
    for times in arcs.values():
        times.sort(); assert len(times)<=540 and all(b-a>=2-1e-8 for a,b in zip(times,times[1:]))
    min_balance=0.; delivered=0.; time_weight=0.
    for rid,r in enumerate(routes):
        for step in range(len(r["path"])-1):
            balance=r["tonnes_day"] if step==0 else 0.
            for _,_,delta in sorted(schedules[rid,step]):
                balance+=delta; min_balance=min(min_balance,balance)
            assert balance>=-1e-6
        for t,m in arrivals[rid,len(r["path"])-2]:
            if t<=1080: delivered+=m; time_weight+=m*t
    s=read(f"results/operation-handling-{handling}/summary.json")
    assert abs(s["delivered_t"]-delivered)<1e-5
    assert abs(s["mean_delivery_time_delivered_min"]-time_weight/delivered)<1e-6
    initial=sum(r["tonnes_day"] for r in routes)
    assert abs(initial-delivered-s["queued_t"]-s["in_transit_or_handling_t"])<1e-5
    return dict(status="PASS",handling_min=handling,trains_checked=len(trains),
        route_precedence_min_balance_t=min_balance,delivered_reconstruction_difference_t=abs(s["delivered_t"]-delivered),
        headway="PASS",station_dispatch="PASS",payload="PASS",route_continuity="PASS",
        terminal_completeness="FAIL_POLICY",scope="valid legal partial schedule; no full daily-clearing certificate")


def phase_audit(d,routes):
    plan=read("results/q4-build-plan.json"); annual=read("results/q4-annual.json")
    nodes=d["nodes"]; idx={n["id"]:i for i,n in enumerate(nodes)}; N=len(nodes)
    edge_by_id={e["id"]:e for e in d["edges"]}; pair={tuple(sorted([idx[e["u"]],idx[e["v"]]])):e for e in d["edges"]}
    assert len(plan["tunnels"])==len(edge_by_id)==len({b["tunnel"] for b in plan["tunnels"]})
    commissions={}
    for b in plan["tunnels"]:
        e=edge_by_id[b["tunnel"]]
        assert (b["u"],b["v"])==(e["u"],e["v"])
        assert abs(sum(b["annual_work_km"])-e["length_km"])<1e-7
        assert sum(b["annual_work_km"][:b["commission_year"]])>=e["length_km"]-1e-7
        assert sum(b["annual_work_km"][:b["commission_year"]-1])<e["length_km"]-1e-7
        for endpoint in [b["u"],b["v"]]: commissions[endpoint]=min(commissions.get(endpoint,8),b["commission_year"])
    with (RUN/"inputs/locations.csv").open(encoding="utf-8") as f: loc=list(csv.DictReader(f))
    ids={int(r["id"]):i for i,r in enumerate(loc)}; D=np.zeros((114,114))
    with (RUN/"inputs/directed-demand.csv").open(encoding="utf-8") as f:
        for row in csv.DictReader(f): D[ids[int(row["origin"])],ids[int(row["destination"])]]=float(row["tonnes_per_day"])
    U=D.copy(); np.fill_diagonal(U,0); M=np.zeros((114,N)); M[:4,:4]=np.eye(4); M[4:,4+d["n_primary"]:]=d["allocation"]
    B=M.T@U@M; gamma=np.array([float(r["congestion"]) for r in loc[4:]])
    rows=[]
    for saved in annual:
        y=saved["year"]; factor=1.05**y; accept=saved["retained_route_acceptance"]
        built={b["tunnel"] for b in plan["tunnels"] if b["commission_year"]<=y}
        commissioned={name for name,year in commissions.items() if year<=y}
        assert commissioned-set(n["id"] for n in nodes[:4])==set(saved["commissioned_stations"])
        flow=defaultdict(float); served=np.zeros((N,N)); adjacency=defaultdict(set)
        for eid in built:
            e=edge_by_id[eid]; assert e["u"] in commissioned and e["v"] in commissioned
            if e["kind"]=="primary-primary": adjacency[e["u"]].add(e["v"]); adjacency[e["v"]].add(e["u"])
        primaries={name for name in commissioned if name.startswith("P")}; seen=set(); todo=[next(iter(primaries))]
        while todo:
            a=todo.pop()
            if a not in seen: seen.add(a); todo.extend(adjacency[a]-seen)
        assert seen==primaries
        for r in routes:
            pairs=list(zip(r["path"],r["path"][1:]))
            if not all(pair[tuple(sorted(a))]["id"] in built for a in pairs): continue
            amount=r["tonnes_day"]*factor*accept
            served[r["origin_index"],r["destination_index"]]+=amount
            for a in pairs: flow[a]+=amount
        for i,n in enumerate(nodes):
            if i<4 or n["id"] in commissioned: served[i,i]=B[i,i]*factor*accept
        calls=np.zeros(N)
        for a,amount in flow.items():
            count=math.ceil(max(0,amount-1e-7)/(pair[tuple(sorted(a))]["vehicle_tonnes"]*8))
            assert count<=540; calls[a[0]]+=count
        assert calls[4:].max()<=90
        ground=served.sum(0)+served.sum(1)
        assert ground[4+d["n_primary"]:].max()<=3000+1e-5
        assert abs(served.sum()-saved["delivered_endpoint_t_day"])<1e-5
        served_fraction=np.divide(served,B*factor,out=np.zeros_like(B),where=B>1e-10)
        original_served=U*(M@served_fraction@M.T)*factor
        assert abs(original_served.sum()-served.sum())<1e-5
        exchange=D.sum(0)+D.sum(1)
        congestion=gamma*(exchange*factor-original_served.sum(0)-original_served.sum(1))[4:]/exchange[4:]
        assert int((congestion>4+1e-8).sum())==saved["regions_above_basic_freeflow"]
        work=sum(b["annual_work_km"][y-1] for b in plan["tunnels"])
        assert abs(work-plan["annual_target_km"])<1e-6
        rows.append(dict(year=y,status="PASS_CONDITIONAL_STATIC_FALLBACK_ACCOUNTING",completed_tunnels=len(built),
            source_disaggregation_residual_t=abs(original_served.sum()-served.sum()),full_target_pass=saved["full_target_pass"]))
    return dict(status="PASS",years=rows,station_commission_year=commissions,
        limitation="Stations assumed buildable by earliest tunnel completion; station construction duration/budget absent. All eight full service targets fail.")


if __name__=="__main__":
    d=read("results/primary/design.json")
    with gzip.open(RUN/"results/primary/routes.json.gz","rt",encoding="utf-8") as f: routes=json.load(f)
    out=dict(operations=[operation_audit(d,routes,h) for h in [0,12]],phasing=phase_audit(d,routes))
    (RUN/"results/independent-operation-phase-audit.json").write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"operations":out["operations"],"phasing":out["phasing"]["status"]},indent=2))
