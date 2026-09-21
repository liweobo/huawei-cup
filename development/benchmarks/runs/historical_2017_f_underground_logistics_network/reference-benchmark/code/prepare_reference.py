"""Freeze the comparison, then acquire exactly the user-authorized PDF set."""
import hashlib
import json
import subprocess
import urllib.parse
import urllib.request
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; REPO=ROOT.parents[4]
NAMES=["F10256001.pdf","F10294003.pdf","F10486024.pdf","F10703002.pdf","F10710008.pdf","F90005027.pdf","FK0263.pdf"]


def sha(p):
    with p.open("rb") as f: return hashlib.file_digest(f,"sha256").hexdigest()


def dump(name,obj):
    (ROOT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")


def git(*args):
    return subprocess.check_output(["git",*args],cwd=REPO).decode("utf-8")


def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":"2017F-posthoc-reference-audit","Accept":"application/vnd.github+json"})
    with urllib.request.urlopen(req,timeout=90) as r: return r.read()


if __name__=="__main__":
    freeze=ROOT/"pre-reference-freeze.json"
    if not freeze.exists():
        prefix=ROOT.relative_to(REPO).as_posix()+"/"
        names=set(n for n in git("ls-files","--cached","--others","--exclude-standard","-z").split("\0") if n and not n.startswith(prefix))
        for sibling in ["run-001","source-recovery","run-002-source-complete"]:
            source_manifest=ROOT.parent/sibling/"source-manifest.json"
            if source_manifest.exists():
                data=json.loads(source_manifest.read_text(encoding="utf-8"))
                for f in data.get("files",[]):
                    p=source_manifest.parent/f["path"]
                    if p.is_file(): names.add(p.relative_to(REPO).as_posix())
        previous=json.loads((ROOT.parent/"run-002-source-complete/integrity-before.json").read_text(encoding="utf-8"))
        names.update(previous["files"])
        protected=["skill"]+[str((ROOT.parent/s).relative_to(REPO)).replace("\\","/") for s in ["run-001","source-recovery","run-002-source-complete"]]
        dump("pre-reference-freeze.json",dict(created_at=datetime.now(timezone.utc).isoformat(),
            head=git("rev-parse","HEAD").strip(),trees={p:git("rev-parse","HEAD:"+p).strip() for p in protected},
            frozen_summary_sha256=sha(ROOT/"current-skill-solution.md"),
            files={n:sha(REPO/n) for n in sorted(names)},
            initial_git_status=git("status","--short"),
            scope="all tracked/nonignored prior artifacts; prior integrity-set files; original source bytes; no cache modifications permitted",
            reference_methods_read_before_summary=False))
    assert sha(ROOT/"current-skill-solution.md")==json.loads(freeze.read_text(encoding="utf-8"))["frozen_summary_sha256"]
    manifest_path=ROOT/"reference-manifest.json"
    if manifest_path.exists():
        for f in json.loads(manifest_path.read_text(encoding="utf-8"))["files"]: assert sha(ROOT/f["path"])==f["sha256"]
        print("Existing verified reference set retained"); raise SystemExit
    commit=json.loads(get("https://api.github.com/repos/zhanwen/MathModel/commits/master"))["sha"]
    folder="国赛论文/2017年优秀论文/F"
    listing_url="https://api.github.com/repos/zhanwen/MathModel/contents/"+urllib.parse.quote(folder)+"?ref="+commit
    listing=json.loads(get(listing_url))
    files=[f for f in listing if f["type"]=="file" and f["name"].lower().endswith(".pdf")]
    assert sorted(f["name"] for f in files)==sorted(NAMES)
    (ROOT/"work/pdfs").mkdir(parents=True,exist_ok=True)
    records=[]
    for f in sorted(files,key=lambda f:f["name"]):
        url="https://raw.githubusercontent.com/zhanwen/MathModel/"+commit+"/"+urllib.parse.quote(folder+"/"+f["name"])
        data=get(url); assert data[:5]==b"%PDF-"
        blob=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest(); assert blob==f["sha"]
        path=ROOT/"work/pdfs"/f["name"]; path.write_bytes(data)
        record=dict(reference_id=f["name"][:-4],filename=f["name"],url=url,path=path.relative_to(ROOT).as_posix(),
            git_blob_sha=blob,sha256=sha(path),bytes=len(data),download_date=datetime.now(timezone.utc).isoformat(),
            source_type="PUBLIC_REPOSITORY_EXCELLENT_PAPER_REFERENCE_SET",award_level="UNKNOWN",award_verified=False)
        records.append(record); print(f["name"],len(data),flush=True)
    dump("reference-manifest.json",dict(repository_commit=commit,listing_url=listing_url,
        reference_set_url="https://github.com/zhanwen/MathModel/tree/master/"+urllib.parse.quote(folder),
        files=records,reference_count=len(records),ground_truth=False))
