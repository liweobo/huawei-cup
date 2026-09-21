"""Baseline, consolidated primary, and bounded physical-tunnel improvement."""
import copy
import time
import yaml
from network_model import RUN,construct_layout,initial_edges,solve,save_solution,dump

record_path=RUN/"experiment-record.yaml"
record=yaml.safe_load(record_path.read_text(encoding="utf-8")); record["status"]="RUNNING"; record["updated_by_workflow"]="run_experiment"
record_path.write_text(yaml.safe_dump(record,allow_unicode=True,sort_keys=False),encoding="utf-8")

for name,consolidate,target in [("baseline",False,2000),("q1-primary",True,1800)]:
    layout,B=construct_layout(consolidate,target); edges=initial_edges(layout,B=B)
    print("START",name,"stations",layout["n_primary"],"edges",len(edges),flush=True)
    solution=solve(layout,edges,B,seconds=120)
    if name=="q1-primary" and not solution["feasible"]:
        dump(RUN/"results/attempt-consolidated-1800.json",solution["meta"])
        for fallback in [1500,1200]:
            layout,B=construct_layout(True,fallback); edges=initial_edges(layout,B=B)
            solution=solve(layout,edges,B,seconds=120)
            dump(RUN/f"results/attempt-consolidated-{fallback}.json",solution["meta"])
            print("FALLBACK",fallback,solution["meta"],flush=True)
            if solution["feasible"]: break
    save_solution(name,layout,edges,solution)
    if not solution["feasible"]: raise RuntimeError((name,solution["meta"]))

before=solution["cost"]["total_daily_yuan"]; trace=[]; start=time.perf_counter()
# High-capital park links are screened, but only complete feasible re-routing can update the incumbent.
candidates=sorted((e for e in edges if e["kind"]=="park-primary"),key=lambda e:e["length_km"]*e["price_yuan_per_km"],reverse=True)[:8]
for iteration,edge in enumerate(candidates,1):
    trial=[e for e in edges if e["id"]!=edge["id"]]
    result=solve(layout,trial,B,seconds=60)
    old=solution["cost"]["total_daily_yuan"]
    new=result.get("cost",{}).get("total_daily_yuan")
    accept=bool(result["feasible"] and new<old-1e-6)
    if accept: edges=trial; solution=result
    item={"iteration":iteration,"move_family":"delete_physical_park_tunnel_and_resolve_all_flows","candidate_id":edge["id"],
          "feasible":result["feasible"],"solver_status":result["meta"]["solver_status"],"objective":new,"incumbent_before":old,
          "incumbent_after":solution["cost"]["total_daily_yuan"],"accepted":accept,"reason":"feasible_realized_cost_improvement" if accept else "rejected_without_penalty", "seconds":result["meta"]["seconds"]}
    trace.append(item); print("MOVE",item,flush=True)
save_solution("primary",layout,edges,solution)
dump(RUN/"results/search-trace.json",{"contract":{"status":"PASS","objective_direction":"MINIMIZE","incumbent_source":"q1-primary",
      "incumbent_feasible":"STATIC_FEASIBLE_ONLY","move_families":[{"name":"delete_park_tunnel","decision_component":"physical_build_selection","rationale":"Reduce large construction depreciation with capacity-aware rerouting"}],
      "candidate_realization":"fixed-design multicommodity LP","feasibility_check":"flow, line, reserved station calls, hierarchy and connectivity",
      "acceptance_rule":"strictly lower realized total daily cost and static feasibility","incumbent_update_rule":"monotone minimum","search_budget":"8 candidate LPs, 60 seconds each","stopping_rule":"budgeted candidate list exhausted","deterministic":True},
      "trace":trace,"evaluated_moves":len(trace),"feasible_moves":sum(t["feasible"] for t in trace),"accepted_moves":sum(t["accepted"] for t in trace),
      "incumbent_updates":sum(t["accepted"] for t in trace),"objective_before":before,"objective_after":solution["cost"]["total_daily_yuan"],
      "termination_reason":"MAX_CANDIDATE_EVALUATIONS","runtime_seconds":time.perf_counter()-start})
