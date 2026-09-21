"""New eight-node oracle; no prior-run fixture or synthetic result imported."""
import math
import numpy as np
from network_model import solve,decompose


def tiny():
    ids=["K1","K2","K3","K4","P0","P1","S0","S1"]
    nodes=[{"id":n,"type":"park" if i<4 else "primary" if i<6 else "secondary"} for i,n in enumerate(ids)]
    pairs=[(0,4,1),(1,5,2),(2,4,5),(3,5,5),(4,5,2),(4,6,1),(5,7,1)]
    edges=[{"id":f"E{i}","u":ids[u],"v":ids[v],"length_km":length,"vehicle_tonnes":10 if u<4 else 5,"price_yuan_per_km":4e8 if u<4 else 3e8} for i,(u,v,length) in enumerate(pairs)]
    B=np.zeros((8,8)); B[0,7]=10.; B[7,0]=4.
    return {"nodes":nodes,"n_primary":2,"n_secondary":2,"access_tonne_km_day":0},edges,B


def test_shortest_flow_physical_cost_oracle():
    L,E,B=tiny(); s=solve(L,E,B)
    assert s["feasible"]
    assert math.isclose(s["cost"]["underground_transport_yuan_day"],56,abs_tol=1e-8)
    assert math.isclose(s["cost"]["tunnel_capital_yuan"],13*4e8+4*3e8,abs_tol=1e-8)
    assert s["meta"]["max_flow_balance"]<1e-8
    paths=decompose(s)
    assert {tuple(p["path"]) for p in paths}=={(0,4,5,7),(7,5,4,0)}


def test_physical_removal_eliminates_both_directions():
    L,E,B=tiny(); s=solve(L,[e for e in E if e["id"]!="E4"],B)
    assert not s["feasible"] and s["meta"]["solver_status"]=="INFEASIBLE"


def test_source_orientation_not_averaged():
    L,E,B=tiny(); s=solve(L,E,B); paths=decompose(s)
    assert sum(p["tonnes_day"] for p in paths if p["origin_index"]==0)==10
    assert sum(p["tonnes_day"] for p in paths if p["origin_index"]==7)==4


def test_hard_capacity_rejects_not_penalizes():
    L,E,B=tiny(); B[0,7]=10000
    assert not solve(L,E,B)["feasible"]
