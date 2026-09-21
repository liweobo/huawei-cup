"""Run scoped regressions and hash-only frozen-history checks."""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime,timezone
from pathlib import Path

RUN=Path(__file__).resolve().parents[1]; REPO=RUN.parents[4]


def sha(path):
    with path.open("rb") as f: return hashlib.file_digest(f,"sha256").hexdigest()


def dump(name,data):
    (RUN/name).write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")


def integrity():
    before=json.loads((RUN/"integrity-before.json").read_text(encoding="utf-8"))
    changed=[n for n,h in before["files"].items() if not (REPO/n).is_file() or sha(REPO/n)!=h]
    sources=json.loads((RUN/"source-manifest.json").read_text(encoding="utf-8"))
    source_checks=[dict(artifact_id=f["artifact_id"],path=f["path"],sha256=sha(RUN/f["path"]),pass_hash=sha(RUN/f["path"])==f["sha256"]) for f in sources["files"]]
    trees={p:subprocess.check_output(["git","rev-parse","HEAD:"+p],cwd=REPO,text=True).strip() for p in before["trees"]}
    diff=subprocess.check_output(["git","diff","--name-only",before["head"],"--"],cwd=REPO,text=True).splitlines()
    prefix=RUN.relative_to(REPO).as_posix()+"/"
    external_diff=[p for p in diff if not p.startswith(prefix)]
    passed=not changed and not external_diff and trees==before["trees"] and all(x["pass_hash"] for x in source_checks)
    out=dict(status="PASS" if passed else "FAIL",starting_head=before["head"],current_head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=REPO,text=True).strip(),
        prior_files_hashed=len(before["files"]),changed_prior_files=changed,protected_trees_before=before["trees"],protected_trees_after=trees,
        outside_run_tracked_diff=external_diff,source_hash_checks=source_checks,
        scope=before["scope"],blind_boundary="prior histories hash-only; no2017F solution-source reads")
    dump("integrity-after.json",out); print(json.dumps(out,indent=2)); assert passed


def tests():
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    temp=RUN/"work"/f"test-temp-{stamp}"; temp.mkdir(parents=True)
    env=dict(os.environ,TEMP=str(temp),TMP=str(temp),PYTHONDONTWRITEBYTECODE="1",PYTHONUTF8="1")
    logs=RUN/"validation-results"; logs.mkdir(exist_ok=True)
    commands=[("development-tests",["-m","pytest","development/tests","-q","-p","no:cacheprovider","--basetemp",str(temp/"pytest-dev")]),
        ("network-tests",["-m","pytest",str(RUN/"code/test_network_components.py"),str(RUN/"code/test_operation.py"),"-q","-p","no:cacheprovider","--basetemp",str(temp/"pytest-network")])]
    for name in ["routing_test","behavior_contract_test","trajectory_test","trajectory_safety_test","problem_facts_test","historical_artifact_test"]:
        commands.append((name,[f"development/harness/{name}.py"]))
    results=[]
    for name,args in commands:
        command=[sys.executable,"-X","utf8","-B",*args]; start=time.perf_counter()
        result=subprocess.run(command,cwd=REPO,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding="utf-8",timeout=900)
        (logs/f"{name}.log").write_text(result.stdout,encoding="utf-8")
        row=dict(name=name,command=command,exit_code=result.returncode,seconds=time.perf_counter()-start,log=f"validation-results/{name}.log")
        results.append(row); print(name,result.returncode,result.stdout[-500:],flush=True)
    dump("validation-results/summary.json",dict(tests=results,default_environment_issue="DEFAULT_PYTEST_ENVIRONMENT_ISSUE_EXISTING",
        default_collection="Not rerun: excluded .tmp checkout and frozen duplicate smoke modules; no repair or deletion",
        skill_only_self_contained="included test_skill_self_contained.py and test_repository_packaging.py in development/tests"))
    assert all(r["exit_code"]==0 for r in results)


if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("mode",choices=["tests","integrity"]); args=p.parse_args()
    tests() if args.mode=="tests" else integrity()
