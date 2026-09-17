"""Source-only acquisition and immutable-input audit for the 2022C blind run."""
from pathlib import Path
import hashlib
import json
import subprocess
import urllib.request
import urllib.parse
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[4]
BENCH = "historical_2022_c_buffer_scheduling"
RUN = BENCH + "/run-001"
SOURCE_PATH = "国赛试题/2022年研究生数学建模竞赛试题/C"
SOURCE = "https://github.com/zhanwen/MathModel/tree/master/" + SOURCE_PATH

def dump(path, obj):
    dest = ROOT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def git(*args):
    return subprocess.check_output(["git", *args], cwd=REPO, text=True, encoding="utf-8").strip()

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def snapshot():
    paths = git("ls-files", "-z").split("\0")
    selected = [p for p in paths if p and (p.startswith("skill/") or p.startswith("development/benchmarks/") or "2023e" in p.lower())]
    files = {p: sha(REPO / p) for p in selected}
    skill = {p: h for p, h in files.items() if p.startswith("skill/")}
    return {"head": git("rev-parse", "HEAD"), "branch": git("branch", "--show-current"),
            "skill_git_tree": git("rev-parse", "HEAD:skill"),
            "skill_content_sha256": hashlib.sha256(json.dumps(skill, sort_keys=True).encode()).hexdigest(),
            "files": files}

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "2022C-blind-source-audit"})
    with urllib.request.urlopen(req, timeout=90) as response:
        return response.read()

def main():
    if (ROOT / "integrity-before.json").exists():
        raise RuntimeError("Already prepared; refusing to overwrite frozen input or before snapshot")
    dump("integrity-before.json", snapshot())
    dump("workspace-manifest.yaml", {
        "schema_version": 2, "isolation_mode": "repository_scoped_blind_run",
        "benchmark_id": BENCH, "run_id": RUN, "active_run_id": RUN,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "allowed_write_root": str(ROOT), "writable_root": str(ROOT),
        "allowed_read_roots": [str(ROOT), str(REPO / "skill")],
        "developer_repository_visible": True, "prior_run_artifacts_visible": True,
        "visibility_note": "Repository visible; prior results not used as modeling inputs. No platform clean-room claim.",
        "immutable_inputs": []})
    api = "https://api.github.com/repos/zhanwen/MathModel/contents/" + urllib.parse.quote(SOURCE_PATH) + "?ref=master"
    items = json.loads(get(api))
    expected = ["汽车制造公司涂装-总装缓存区调序调度优化问题.docx"] + [f"附件{i}.xlsx" for i in range(1, 5)]
    selected = {item["name"]: item for item in items if item["name"] in expected}
    if set(selected) != set(expected):
        raise RuntimeError(f"Source directory names: {[i['name'] for i in items]}")
    records = []
    for name in expected:
        item = selected[name]
        content = get(item["download_url"])
        dest = ROOT / "raw" / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(content)
        with zipfile.ZipFile(dest) as archive:
            bad = archive.testzip()
            essential = "word/document.xml" if name.endswith("docx") else "xl/workbook.xml"
            assert bad is None and essential in archive.namelist()
        blob_sha = hashlib.sha1(f"blob {len(content)}\0".encode() + content).hexdigest()
        assert blob_sha == item["sha"] and len(content) == item["size"]
        records.append({"source_artifact_id": f"INPUT-{len(records)+1:02}", "path": "raw/" + name,
                        "filename": name, "source_url": item["html_url"], "download_url": item["download_url"],
                        "sha256": sha(dest), "git_blob_sha1": blob_sha, "bytes": len(content),
                        "zip_crc": "PASS", "required_ooxml_part": essential})
    dump("source-provenance.json", {"source_status": "ACCEPTED", "independently_official_verified": False,
         "reason": "User-authorized mirror; raw files match GitHub blob SHA1 and size, OOXML CRC verified.",
         "directory_url": SOURCE, "listing_api_url": api, "accessed_at": datetime.now(timezone.utc).isoformat(),
         "excellent_solutions_accessed": False, "files": records})
    manifest = json.loads((ROOT / "workspace-manifest.yaml").read_text(encoding="utf-8"))
    manifest["immutable_inputs"] = records
    dump("workspace-manifest.yaml", manifest)
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with zipfile.ZipFile(ROOT / "raw" / expected[0]) as archive:
        document = ET.fromstring(archive.read("word/document.xml"))
        lines = []
        for i, element in enumerate(document.find("w:body", ns), 1):
            strings = [node.text or "" for node in element.iter() if node.tag.endswith("}t")]
            lines.append(f"[B{i:03}] " + " | ".join(strings))
        dest = ROOT / "extracted"
        dest.mkdir(exist_ok=True)
        (dest / "problem.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        for name in archive.namelist():
            if name.startswith("word/media/"):
                (dest / Path(name).name).write_bytes(archive.read(name))
    print(json.dumps({"files": records, "problem": "\n".join(lines)}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
