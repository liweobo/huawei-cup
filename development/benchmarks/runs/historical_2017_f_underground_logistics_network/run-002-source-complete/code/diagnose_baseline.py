"""Retain the rejected topology and test capacity cause without promoting relaxations."""
import json
from network_model import RUN,construct_layout,initial_edges,solve,dump

prior=json.loads((RUN/"results/baseline/solver.json").read_text(encoding="utf-8"))
dump(RUN/"results/attempt-001-rejected.json",{"status":"REJECTED_BEFORE_FORMAL_RESULT","settings":{"consolidate":False,"target":3000,"k_nearest":5,"od_shortcuts":False},"solver":prior})
L,B=construct_layout(False,3000)
relax=solve(L,initial_edges(L),B,seconds=90,dispatch_limit=900)
dump(RUN/"results/capacity-relaxation-diagnostic.json",{"not_admissible_as_answer":True,"relaxed_limit":900,"original_limit":90,"meta":relax["meta"]})
print("RELAX",relax["meta"],flush=True)
for target in [3000,2400,2000]:
    L,B=construct_layout(False,target)
    S=solve(L,initial_edges(L,B=B),B,seconds=120)
    dump(RUN/f"results/attempt-baseline-{target}.json",{"target":target,"od_shortcuts":True,"feasible":S["feasible"],"meta":S["meta"]})
    print("CANDIDATE",target,S["meta"],flush=True)
    if S["feasible"]: break
