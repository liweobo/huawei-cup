"""Independent final reconstruction. Does not import solver/model helpers."""
import csv
import gzip
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
import numpy as np

RUN=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(RUN/"work/deps"))
import networkx as nx
import xlrd


def audit(name):
    folder=RUN/"results"/name
    design=json.loads((folder/"design.json").read_text(encoding="utf-8"))
    nodes=design["nodes"]; N=len(nodes); index={r["id"]:i for i,r in enumerate(nodes)}
    assert len(index)==N
    source=xlrd.open_workbook(next((RUN/"work/source").glob("*.xls")))
    od=source.sheet_by_name("现状全天OD"); attr=source.sheet_by_name("各区域中心点及面积")
    ids=[int(attr.cell_value(r,0)) for r in range(1,115)]; A=design["allocation"]; n=design["n_primary"]
    endpoint={i:[(i,1.)] for i in range(4)}
    for i in range(4,114): endpoint[i]=[(4+n+s,float(A[i-4][s])) for s in range(n) if A[i-4][s]>1e-10]
    assert all(abs(sum(v for _,v in endpoint[i])-1)<1e-9 for i in range(114))
    B=np.zeros((N,N)); ground=np.zeros(N); access=0.; diagonal=0.; original_total=0.
    max_source_csv_error=0.
    with (RUN/"inputs/directed-demand.csv").open(encoding="utf-8") as f:
        rows=list(csv.DictReader(f))
    source_index={v:i for i,v in enumerate(ids)}
    for row in rows:
        i=source_index[int(row["origin"])]; j=source_index[int(row["destination"])]
        max_source_csv_error=max(max_source_csv_error,abs(float(row["tonnes_per_day"])-od.cell_value(j+1,i+1)))
    for i in range(114):
        for j in range(114):
            tonnes=float(od.cell_value(j+1,i+1)); original_total+=tonnes
            if i==j: diagonal+=tonnes; continue
            for a,wa in endpoint[i]:
                for b,wb in endpoint[j]: B[a,b]+=tonnes*wa*wb
            for endpoint_i in [i,j]:
                if endpoint_i<4: continue
                x=float(attr.cell_value(endpoint_i+1,3))/1000; y=float(attr.cell_value(endpoint_i+1,4))/1000
                for s,w in endpoint[endpoint_i]:
                    ground[s]+=tonnes*w
                    distance=math.hypot(nodes[s]["x_km"]-x,nodes[s]["y_km"]-y)
                    assert distance<=3+1e-8
                    access+=tonnes*w*distance
    original_accounting=abs(B.sum()+diagonal-original_total)
    graph=nx.Graph(); graph.add_nodes_from(index)
    physical={}; lengths={}; capital=0.; allowed_arcs={}; primary_ids=[v["id"] for v in nodes if v["type"]=="primary"]
    for e in design["edges"]:
        assert e["id"] not in physical; physical[e["id"]]=e
        u,v=e["u"],e["v"]; assert u!=v and not graph.has_edge(u,v)
        a,b=nodes[index[u]],nodes[index[v]]
        kindset={a["type"],b["type"]}
        assert kindset in [{"park","primary"},{"primary"},{"primary","secondary"}]
        if "secondary" in kindset:
            child=a if a["type"]=="secondary" else b; parent=b if child is a else a
            assert child["parent_primary"]==parent["id"]
        length=math.hypot(a["x_km"]-b["x_km"],a["y_km"]-b["y_km"])
        assert math.isfinite(length) and length>0 and abs(length-e["length_km"])<1e-9
        price=4e8 if "park" in kindset else 3e8
        payload=80. if "park" in kindset else 40.
        assert e["tracks"]==2 and e["price_yuan_per_km"]==price and e["vehicle_tonnes"]==payload/8
        capital+=length*price; lengths[e["id"]]=length
        allowed_arcs[u,v]=(e["id"],payload); allowed_arcs[v,u]=(e["id"],payload)
        graph.add_edge(u,v,length=length)
    assert nx.is_connected(graph.subgraph(primary_ids)) and nx.is_connected(graph)
    for node in nodes:
        if node["type"]=="secondary": assert list(graph.neighbors(node["id"]))==[node["parent_primary"]]
    balances=np.zeros((N,N)); directed=defaultdict(float); commodity=defaultdict(float); transport=0.
    with gzip.open(folder/"commodity-flows.csv.gz","rt",encoding="utf-8") as f:
        for row in csv.DictReader(f):
            k,u,v=row["origin"],row["u"],row["v"]; x=float(row["tonnes_day"])
            assert x>=0 and math.isfinite(x)
            eid,cap=allowed_arcs[u,v]; assert eid==row["physical_tunnel"]
            assert not (nodes[index[u]]["type"]=="park" and k!=u)
            balances[index[k],index[u]]+=x; balances[index[k],index[v]]-=x
            directed[u,v]+=x; commodity[k,u,v]+=x; transport+=x*lengths[eid]
    expected=-B.copy()
    for i in range(N): expected[i,i]=sum(B[i,j] for j in range(N) if i!=j)
    residual=float(np.max(np.abs(expected-balances)))
    calls=defaultdict(int); line_violation=0.
    for (u,v),(eid,payload) in allowed_arcs.items():
        t=math.ceil(max(0,directed[u,v]-1e-7)/payload)
        calls[u]+=t; line_violation=max(line_violation,t-540)
    station_violation=max(0,max(calls[r["id"]]-90 for r in nodes if r["type"]!="park"))
    ground_violation=max(0,max(ground[i]-(3000 if nodes[i]["type"]=="secondary" else 4000) for i in range(4,N)))
    node_exchange_error=max(abs(ground[i]-nodes[i].get("ground_exchange_t_day",0)) for i in range(4,N))
    with gzip.open(folder/"routes.json.gz","rt",encoding="utf-8") as f: routes=json.load(f)
    route_od=np.zeros((N,N)); route_flow=defaultdict(float)
    for row in routes:
        path=row["path"]; k=row["origin_index"]; d=row["destination_index"]; x=row["tonnes_day"]
        assert path[0]==k and path[-1]==d and len(path)==len(set(path))
        assert all(nodes[q]["type"]!="park" for q in path[1:-1])
        route_od[k,d]+=x
        for u,v in zip(path,path[1:]):
            assert (nodes[u]["id"],nodes[v]["id"]) in allowed_arcs
            route_flow[nodes[k]["id"],nodes[u]["id"],nodes[v]["id"]]+=x
    expected_routes=B.copy(); np.fill_diagonal(expected_routes,0)
    path_error=float(abs(route_od-expected_routes).max())
    flow_path_error=max(abs(commodity[key]-route_flow[key]) for key in set(commodity)|set(route_flow))
    station_capital=sum(1.5e8 if r["type"]=="primary" else 1e8 if r["type"]=="secondary" else 0 for r in nodes)
    objective=transport+access+(capital+station_capital)*.01/365
    difference=abs(objective-design["cost"]["total_daily_yuan"])
    ratios=json.loads((folder/"transfer-ratios.json").read_text(encoding="utf-8"))
    ratio_error=0.
    for row in ratios["by_park"]:
        park=index[row["park"]]; nearest=min((index[q] for q in primary_ids),key=lambda p:((nodes[p]["x_km"]-nodes[park]["x_km"])**2+(nodes[p]["y_km"]-nodes[park]["y_km"])**2,p))
        assert nodes[nearest]["id"]==row["nearest_primary"]
        num=0.
        for r in routes:
            if r["origin_index"]==park and nearest in r["path"]:
                rest=r["path"][r["path"].index(nearest)+1:]
                if any(nodes[q]["type"]=="primary" for q in rest): num+=r["tonnes_day"]
        denom=sum(float(od.cell_value(j+1,park+1)) for j in range(114))
        ratio_error=max(ratio_error,abs(row["denominator_t_day"]-denom),abs(row["numerator_t_day"]-num))
    result={"name":name,"scope":"Independent static network/flow/cost audit, not proof of a timed operating day",
      "source_csv_orientation_error":max_source_csv_error,"source_demand_accounting_residual_t_day":original_accounting,
      "node_count":N,"physical_edge_count":len(physical),"directed_arc_count":len(allowed_arcs),"graph_components":nx.number_connected_components(graph),
      "primary_components":nx.number_connected_components(graph.subgraph(primary_ids)),"isolates":list(nx.isolates(graph)),
      "od_reachability":"PASS_ALL_REQUESTED_ROUTED_ENDPOINT_DEMAND","allocation_coverage":"PASS_ALL_110_REGIONS_CENTRE_COVERED",
      "maximum_flow_conservation_residual_t_day":residual,"maximum_path_od_residual_t_day":path_error,"maximum_path_flow_residual_t_day":flow_path_error,
      "maximum_ground_exchange_violation_t_day":ground_violation,"node_exchange_reconstruction_error_t_day":node_exchange_error,
      "maximum_station_departure_violation":station_violation,"maximum_line_departure_violation":max(0,line_violation),
      "reconstructed_transport_yuan_day":transport,"reconstructed_access_yuan_day":access,"reconstructed_physical_tunnel_capital_yuan":capital,
      "reconstructed_station_capital_yuan":station_capital,"reconstructed_total_yuan_day":objective,"objective_difference_yuan_day":difference,
      "transfer_ratio_component_residual":ratio_error,"physical_cost_counting":"ONCE_PER_TUNNEL","daily_clearing":"NOT_CERTIFIED_BY_THIS_STATIC_AUDIT"}
    checks=[max_source_csv_error<1e-10,original_accounting<1e-6,residual<1e-5,path_error<1e-5,flow_path_error<1e-5,ground_violation<1e-6,node_exchange_error<1e-6,station_violation==0,line_violation<=0,difference<1e-4,ratio_error<1e-6]
    result["status"]="PASS" if all(checks) else "FAIL"
    return result


if __name__=="__main__":
    results=[audit(name) for name in ["baseline","q1-primary","primary"]]
    output=RUN/"results/independent-audit.json"
    output.write_text(json.dumps(results,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(results,indent=2))
    assert all(r["status"]=="PASS" for r in results)
