"""Freeze this run and retain verified originals without reading prior solutions."""
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

RUN = Path(__file__).resolve().parents[1]
REPO = RUN.parents[4]
RECOVERY = RUN.parent / "source-recovery"


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=REPO).decode("utf-8")


def save(p, obj):
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")


if __name__ == "__main__":
    (RUN/"work/source").mkdir(parents=True,exist_ok=True)
    (RUN/"results").mkdir(exist_ok=True)
    freeze=RUN/"integrity-before.json"
    if not freeze.exists():
        prefix=RUN.relative_to(REPO).as_posix()+"/"
        names=set(filter(None,git("ls-files","--cached","--others","--exclude-standard","-z").split("\0")))
        names.update(p.relative_to(REPO).as_posix() for p in RECOVERY.rglob("*") if p.is_file())
        files={n:digest(REPO/n) for n in sorted(names) if not n.startswith(prefix)}
        protected_paths=["skill","development/benchmarks/runs/historical_2017_f_underground_logistics_network/run-001",
                         "development/benchmarks/runs/historical_2017_f_underground_logistics_network/source-recovery"]
        save(freeze,{"created_at":datetime.now(timezone.utc).isoformat(),"head":git("rev-parse","HEAD").strip(),
                     "trees":{p:git("rev-parse","HEAD:"+p).strip() for p in protected_paths},"files":files,
                     "status":git("status","--short","--untracked-files=all"),
                     "scope":"All tracked/nonignored pre-existing files, plus every local source-recovery file; hash-only history access"})
    manifest=json.loads((RECOVERY/"attachment-manifest.json").read_text(encoding="utf-8"))
    kept=[]
    for f in manifest["files"]:
        original=RECOVERY/f["path"]
        assert digest(original)==f["sha256"]
        target=RUN/"work/source"/f["filename"]
        if target.exists():
            assert digest(target)==f["sha256"]
        else:
            shutil.copyfile(original,target)
        kept.append({"artifact_id":f["id"],"path":target.relative_to(RUN).as_posix(),"sha256":digest(target),
                     "bytes":target.stat().st_size,"source_url":f["source_url"],"classification":f["confidence"]})
    save(RUN/"source-manifest.json",{"run_id":RUN.name,"source_page":manifest["source_page"],"files":kept,
         "retention":"Local byte-preserved originals in ignored work/source; no change to prior metadata-only delivery policy"})
    print("Frozen",json.loads(freeze.read_text(encoding="utf-8"))["head"],"; retained",len(kept),"verified original files")
