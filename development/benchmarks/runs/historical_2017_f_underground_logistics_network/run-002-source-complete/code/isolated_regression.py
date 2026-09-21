"""Byte-identical test replica; all writes remain in this run's ignored work root."""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

RUN=Path(__file__).resolve().parents[1]; REPO=RUN.parents[4]
def extended(p):
    return Path("\\\\?\\"+str(p)) if os.name=="nt" else p

copy=extended(RUN/"work/r"); copy.mkdir(parents=True,exist_ok=True)
temp=extended(RUN/"work"/f"t{int(time.time())}"); temp.mkdir()
prefixes=["skill/","development/tests/","development/tooling/","development/harness/",
    "development/benchmarks/problems/2023/E/raw/",
    "development/benchmarks/runtime/historical_2023_e_hemorrhagic_stroke/run-001/code/"]
names=subprocess.check_output(["git","ls-files","-z"],cwd=REPO).decode().split("\0")
manifest=[]
for name in names:
    if not any(name.startswith(p) for p in prefixes): continue
    source=REPO/name; target=copy/name; target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source,target)
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    assert digest==hashlib.sha256(target.read_bytes()).hexdigest()
    manifest.append(dict(path=name,sha256=digest))
env=dict(os.environ,TEMP=str(temp),TMP=str(temp),PYTHONPATH=str(copy),PYTHONDONTWRITEBYTECODE="1",PYTHONUTF8="1")
commands=[("development-tests-isolated",["-m","pytest","development/tests","-q","-p","no:cacheprovider","--basetemp",str(temp/"d")],copy),
    ("network-tests-isolated",["-m","pytest",str(RUN/"code/test_network_components.py"),str(RUN/"code/test_operation.py"),"-q","-p","no:cacheprovider","--basetemp",str(temp/"n")],REPO)]
rows=[]
for name,args,cwd in commands:
    command=[sys.executable,"-X","utf8","-B",*args]; start=time.perf_counter()
    r=subprocess.run(command,cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding="utf-8",timeout=900)
    (RUN/f"validation-results/{name}.log").write_text(r.stdout,encoding="utf-8")
    rows.append(dict(name=name,command=command,cwd=str(cwd),exit_code=r.returncode,seconds=time.perf_counter()-start))
    print(name,r.returncode,r.stdout[-700:],flush=True)
(RUN/"validation-results/isolated-summary.json").write_text(json.dumps(dict(tests=rows,copied_files=manifest,
    policy="No source modifications, original tracked bytes copied; extended-length Windows paths; temporary outputs outside copied benchmark roots but inside active run work",
    previous_attempt="summary.json retains original environment failures"),indent=2)+"\n",encoding="utf-8")
assert all(r["exit_code"]==0 for r in rows)
