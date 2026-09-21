"""Problem-specific 2017F allocation and fixed-design multicommodity LP."""
import csv
import gzip
import json
import sys
import time
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
from scipy import sparse

RUN=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(RUN/"work/deps"))
import networkx as nx


def dump(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,default=lambda x:x.item() if hasattr(x,"item") else list(x))+"\n",encoding="utf-8")


def load_inputs():
    with (RUN/"inputs/locations.csv").open(encoding="utf-8") as f: locations=list(csv.DictReader(f))
    ids=[int(r["id"]) for r in locations]; index={v:i for i,v in enumerate(ids)}
    xy=np.array([[float(r["x_m"]),float(r["y_m"])] for r in locations])/1000
    D=np.zeros((len(ids),len(ids)))
    with (RUN/"inputs/directed-demand.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f): D[index[int(r["origin"])] , index[int(r["destination"])]]=float(r["tonnes_per_day"])
    return ids,xy,D,locations


def construct_layout(consolidate, target, offset=.25):
    ids,xy,D,loc=load_inputs(); U=D.copy(); np.fill_diagonal(U,0)
    exchange=U.sum(0)+U.sum(1); remaining=exchange[4:].copy(); slots=np.zeros(110,int)
    allocations=[]; sites=[]
    while remaining.max()>1e-7:
        seed=int(np.argmax(remaining)); pos=xy[seed+4]+[.15*slots[seed],0]; slots[seed]+=1
        available=float(target); col=np.zeros(110)
        dist=np.linalg.norm(xy[4:]-pos,axis=1)
        eligible=np.argsort(dist,kind="stable") if consolidate else [seed]
        for i in eligible:
            if dist[i]>3+1e-10 or remaining[i]<=1e-8: continue
            take=min(available,remaining[i]); col[i]=take/exchange[i+4]; remaining[i]-=take; available-=take
            if available<1e-7: break
        assert col.sum()>0
        sites.append((pos,ids[seed+4])); allocations.append(col)
    A=np.array(allocations).T; n=len(sites); N=4+2*n
    M=np.zeros((114,N)); M[:4,:4]=np.eye(4); M[4:,4+n:]=A
    B=M.T@U@M
    nodes=[]
    for i in range(4): nodes.append({"id":f"K{ids[i]}","type":"park","x_km":xy[i,0],"y_km":xy[i,1],"source_id":ids[i],"ground_capacity_t_day":None})
    for s,(pos,seed) in enumerate(sites):
        nodes.append({"id":f"P{s:03}","type":"primary","x_km":pos[0],"y_km":pos[1]+offset,"ground_capacity_t_day":4000.,"ground_exchange_t_day":0.,"source_seed_id":seed})
    for s,(pos,seed) in enumerate(sites):
        weights=A[:,s]; radii=np.linalg.norm(xy[4:]-pos,axis=1)
        nodes.append({"id":f"S{s:03}","type":"secondary","x_km":pos[0],"y_km":pos[1],"source_seed_id":seed,"parent_primary":f"P{s:03}",
                      "ground_capacity_t_day":3000.,"ground_exchange_t_day":float(weights@exchange[4:]),"service_radius_km":float(max(radii[weights>1e-10])),
                      "served_regions":[{"id":ids[i+4],"fraction":float(weights[i]),"centre_distance_km":float(radii[i])} for i in range(110) if weights[i]>1e-10]})
    access=sum(float((A[:,s]*exchange[4:])@np.linalg.norm(xy[4:]-sites[s][0],axis=1)) for s in range(n))
    return {"nodes":nodes,"allocation":A.tolist(),"input_ids":ids,"n_primary":n,"n_secondary":n,"access_tonne_km_day":access,
            "layout_method":"spatial-consolidation" if consolidate else "per-region-baseline","constructive_target_t_day":target,"primary_offset_km":offset,
            "source_offdiagonal_t_day":float(U.sum()),"original_diagonal_surface_t_day":float(np.trace(D)),"station_local_t_day":float(np.trace(B))},B


def initial_edges(layout,k=5,B=None):
    nodes=layout["nodes"]; n=layout["n_primary"]; xy=np.array([[r["x_km"],r["y_km"]] for r in nodes]); pairs={}
    def add(u,v,reason):
        u,v=sorted([u,v]); pairs.setdefault((u,v),[]).append(reason)
    for j in range(n):
        for park in range(4): add(park,4+j,"ASSUMED_PARK_PRIMARY_STRAIGHT_CORRIDOR")
        add(4+j,4+n+j,"OWN_PRIMARY_SECONDARY_FEEDER")
    g=nx.Graph(); g.add_nodes_from(range(4,4+n))
    for i in range(4,4+n):
        for j in range(i+1,4+n): g.add_edge(i,j,weight=float(np.linalg.norm(xy[i]-xy[j])))
        nearest=sorted((j for j in range(4,4+n) if j!=i),key=lambda j:(np.linalg.norm(xy[i]-xy[j]),j))[:k]
        for j in nearest: add(i,j,f"ASSUMED_BACKBONE_SEARCH_SET_KNN_{k}")
    for u,v in nx.minimum_spanning_edges(g,data=False): add(u,v,"CONNECTED_BACKBONE_CONSTRUCTIVE_RULE")
    if B is not None:
        for i in range(n):
            peers=sorted((j for j in range(n) if j!=i),key=lambda j:-(B[4+n+i,4+n+j]+B[4+n+j,4+n+i]))[:2]
            for j in peers: add(4+i,4+j,"TOP_TWO_AGGREGATED_DEMAND_BACKBONE_DESIGN_CANDIDATE")
    out=[]
    for (u,v),why in sorted(pairs.items()):
        kind="park-primary" if u<4 else ("primary-secondary" if v>=4+n else "primary-primary")
        length=float(np.linalg.norm(xy[u]-xy[v])); assert length>1e-7
        out.append({"id":f"T{u:03}_{v:03}","u":nodes[u]["id"],"v":nodes[v]["id"],"kind":kind,"length_km":length,
                    "vehicle_tonnes":10 if kind=="park-primary" else 5,"tracks":2,"price_yuan_per_km":4e8 if kind=="park-primary" else 3e8,
                    "construction_rule":why,"source_status":"ASSUMED_GEOMETRIC_CANDIDATE_SELECTED_AS_BUILT"})
    return out


def solve(layout,edges,B,seconds=60,cars=8,dispatch_limit=90):
    start=time.perf_counter(); nodes=layout["nodes"]; N=len(nodes); n=layout["n_primary"]; idx={r["id"]:i for i,r in enumerate(nodes)}
    arcs=[]
    for e in edges:
        u,v=idx[e["u"]],idx[e["v"]]
        for a,b in [(u,v),(v,u)]: arcs.append((a,b,e["length_km"],e["vehicle_tonnes"]*cars,e["id"]))
    m=len(arcs); origins=[i for i in range(N) if B[i].sum()-B[i,i]>1e-9]; K=len(origins)
    u=np.array([a[0] for a in arcs]); v=np.array([a[1] for a in arcs]); length=np.array([a[2] for a in arcs]); payload=np.array([a[3] for a in arcs])
    incidence=sparse.coo_matrix((np.r_[np.ones(m),-np.ones(m)],(np.r_[u,v],np.r_[np.arange(m),np.arange(m)])),shape=(N,m)).tocsr()
    eq=sparse.kron(sparse.eye(K),incidence,format="csr")
    rhs=[]
    for k in origins:
        r=-B[k].copy(); r[k]=B[k].sum()-B[k,k]; rhs.extend(r)
    aggregation=sparse.kron(np.ones((1,K)),sparse.eye(m),format="csr")
    stations=np.arange(4,N); degree=np.bincount(u,minlength=N)
    disp=sparse.coo_matrix((1/payload,(u,np.arange(m))),shape=(N,m)).tocsr()[4:]
    ub=sparse.vstack([aggregation,sparse.kron(np.ones((1,K)),disp,format="csr")],format="csr")
    capacity=np.r_[540*payload,dispatch_limit-degree[4:]]
    bounds=np.column_stack([np.zeros(K*m),np.full(K*m,np.inf)])
    for a,k in enumerate(origins): bounds[a*m:(a+1)*m,1][(u<4)&(u!=k)]=0
    result=linprog(np.tile(length,K),A_ub=ub,b_ub=capacity,A_eq=eq,b_eq=np.array(rhs),bounds=bounds,method="highs",options={"time_limit":seconds})
    status={0:"OPTIMAL_FIXED_DESIGN_LP",1:"TIME_LIMIT",2:"INFEASIBLE",3:"UNBOUNDED",4:"NUMERICAL_ERROR"}.get(result.status,"UNKNOWN")
    meta={"solver_status":status,"message":result.message,"seconds":time.perf_counter()-start,"variables":K*m,"equality_rows":K*N,"inequality_rows":m+N-4,"commodities":K,"physical_edges":len(edges),"directed_arcs":m,"nodes":N,"cars":cars,"dispatch_limit":dispatch_limit}
    if result.x is None or result.status!=0: return {"meta":meta,"feasible":False}
    flow=result.x.reshape(K,m); total=flow.sum(0); trains=np.ceil(np.maximum(total-1e-7,0)/payload); calls=np.bincount(u,weights=trains,minlength=N)
    max_balance=float(abs(eq@result.x-np.array(rhs)).max()); maxcap=float(max(0,(ub@result.x-capacity).max()))
    static=max_balance<1e-5 and maxcap<1e-5 and calls[4:].max()<=90
    meta.update(max_flow_balance=max_balance,max_lp_capacity_violation=maxcap,max_station_departures=float(calls[4:].max()),
                max_directional_line_departures=float(trains.max()),static_feasible=bool(static),daily_clearing="STATIC_ONLY")
    tunnel_capital=sum(e["length_km"]*e["price_yuan_per_km"] for e in edges)
    station_capital=n*1.5e8+layout["n_secondary"]*1e8
    cost={"underground_transport_yuan_day":float(total@length),"access_proxy_yuan_day":layout["access_tonne_km_day"],
          "tunnel_capital_yuan":tunnel_capital,"station_capital_yuan":station_capital,
          "tunnel_depreciation_yuan_day":tunnel_capital*.01/365,"station_depreciation_yuan_day":station_capital*.01/365}
    cost["total_daily_yuan"]=cost["underground_transport_yuan_day"]+cost["access_proxy_yuan_day"]+cost["tunnel_depreciation_yuan_day"]+cost["station_depreciation_yuan_day"]
    return {"meta":meta,"feasible":bool(static),"cost":cost,"flow":flow,"origins":origins,"arcs":arcs,"total":total,"trains":trains,"calls":calls,"B":B}


def decompose(solution):
    flow=solution["flow"]; arcs=solution["arcs"]; B=solution["B"]; records=[]
    for ki,k in enumerate(solution["origins"]):
        g=nx.DiGraph()
        for a,(u,v,length,cap,eid) in enumerate(arcs):
            if flow[ki,a]>1e-7: g.add_edge(u,v,residual=float(flow[ki,a]),weight=length)
        for dest in range(B.shape[0]):
            rem=float(B[k,dest]) if k!=dest else 0
            while rem>1e-6:
                path=nx.shortest_path(g,k,dest,weight="weight")
                amount=min(rem,min(g[u][v]["residual"] for u,v in zip(path,path[1:])))
                records.append({"origin_index":k,"destination_index":dest,"tonnes_day":amount,"path":path})
                rem-=amount
                for u,v in zip(path,path[1:]):
                    g[u][v]["residual"]-=amount
                    if g[u][v]["residual"]<1e-7: g.remove_edge(u,v)
        assert sum(e["residual"] for _,_,e in g.edges(data=True))<1e-4
    return records


def save_solution(name,layout,edges,solution):
    B=solution.get("B")
    out=RUN/"results"/name; out.mkdir(exist_ok=True)
    dump(out/"solver.json",solution["meta"])
    if not solution["feasible"]: return
    assert solution["feasible"]
    dump(out/"design.json",dict(layout,edges=edges,cost=solution["cost"],status="STATIC_FEASIBLE_CONDITIONAL_DESIGN_NOT_TIMETABLE"))
    with gzip.open(out/"commodity-flows.csv.gz","wt",encoding="utf-8",newline="") as f:
        w=csv.writer(f); w.writerow(["origin","u","v","physical_tunnel","tonnes_day"])
        for ki,k in enumerate(solution["origins"]):
            for a in np.flatnonzero(solution["flow"][ki]>1e-8):
                u,v,_,_,eid=solution["arcs"][a]
                w.writerow([layout["nodes"][k]["id"],layout["nodes"][u]["id"],layout["nodes"][v]["id"],eid,format(solution["flow"][ki,a],".15g")])
    paths=decompose(solution)
    with gzip.open(out/"routes.json.gz","wt",encoding="utf-8") as f: json.dump(paths,f,separators=(",",":"))
    metrics=[]
    for i,node in enumerate(layout["nodes"]):
        item=dict(node,underground_out_t_day=float(solution["total"][[a[0]==i for a in solution["arcs"]]].sum()),
                  underground_in_t_day=float(solution["total"][[a[1]==i for a in solution["arcs"]]].sum()),
                  rounded_departures_day=float(solution["calls"][i]))
        metrics.append(item)
    dump(out/"node-results.json",metrics)
    tunnels=[]
    for j,e in enumerate(edges):
        tunnels.append(dict(e,flow_u_v_t_day=float(solution["total"][2*j]),flow_v_u_t_day=float(solution["total"][2*j+1]),
                            departures_u_v=float(solution["trains"][2*j]),departures_v_u=float(solution["trains"][2*j+1])))
    dump(out/"tunnel-results.json",tunnels)
    ratios=[]; nodes=layout["nodes"]; n=layout["n_primary"]
    for park in range(4):
        nearest=min(range(4,4+n),key=lambda p:((nodes[p]["x_km"]-nodes[park]["x_km"])**2+(nodes[p]["y_km"]-nodes[park]["y_km"])**2,p))
        denom=float(B[park].sum()); numerator=0.
        for r in paths:
            if r["origin_index"]!=park or nearest not in r["path"]: continue
            after=r["path"][r["path"].index(nearest)+1:]
            if any(4<=x<4+n for x in after): numerator+=r["tonnes_day"]
        ratios.append({"park":nodes[park]["id"],"nearest_primary":nodes[nearest]["id"],"nearest_metric":"ASSUMED_EUCLIDEAN_KM",
                       "numerator_t_day":numerator,"denominator_t_day":denom,"ratio":numerator/denom})
    dump(out/"transfer-ratios.json",{"by_park":ratios,"by_primary":[{"primary":nodes[p]["id"],"ratios":[r for r in ratios if r["nearest_primary"]==nodes[p]["id"]],
          "status":"DEFINED_BY_NEAREST_PARK" if any(r["nearest_primary"]==nodes[p]["id"] for r in ratios) else "NOT_APPLICABLE_NO_ASSOCIATED_PARK_DENOMINATOR"} for p in range(4,4+n)]})
    print(name,json.dumps(dict(solution["meta"],cost=solution["cost"],paths=len(paths)),default=float),flush=True)
