"""Acquire only the user-designated 2007A source and freeze protected state."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


RUN = Path(__file__).resolve().parents[1]
REPO = RUN.parents[4]
BENCHMARK_ID = RUN.parent.name
RUN_ID = RUN.name
DIRECTORY = "国赛试题/2007年研究生数学建模竞赛试题"
FILENAME = "2007年A题  建立食品卫生安全保障体系数学模型及改进模型的若干理论问题（终）.doc"
DIRECTORY_URL = f"https://github.com/zhanwen/MathModel/tree/master/{DIRECTORY}"
DIRECTORY_API = (
    "https://api.github.com/repos/zhanwen/MathModel/contents/"
    + urllib.parse.quote(DIRECTORY, safe="/")
    + "?ref=master"
)
EXPECTED_BLOB = "42ab94a3cd6fd90ed59bc13aaa2c0678c4304d44"
PROTECTED = [
    "skill",
    "development/benchmarks/runs/historical_2005_d_stochastic_inventory",
    "development/benchmarks/runs/historical_2011_b_absorbing_material_anechoic_chamber",
    "development/benchmarks/runs/historical_2017_f_underground_logistics_network",
    "development/benchmarks/runs/historical_2020_a_chip_phase_noise",
    "development/benchmarks/runs/historical_2022_c_buffer_scheduling",
    "development/benchmarks/runs/historical_2023_e_hemorrhagic_stroke",
    "development/benchmarks/runs/historical_2024_c_core_loss",
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def git(*args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=check,
    )
    return result.stdout.strip()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def request(url: str) -> bytes:
    quoted = urllib.parse.quote(url, safe=":/?=&%")
    req = urllib.request.Request(
        quoted,
        headers={
            "User-Agent": "2007A-strict-blind-source-audit",
            "Accept": "application/vnd.github+json",
        },
    )
    with urllib.request.urlopen(req, timeout=90) as response:
        return response.read()


def write_json(relative: str, payload: object) -> None:
    path = RUN / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def protected_snapshot() -> dict[str, object]:
    trees: dict[str, str | None] = {}
    for path in PROTECTED:
        result = subprocess.run(
            ["git", "rev-parse", f"HEAD:{path}"],
            cwd=REPO,
            text=True,
            encoding="utf-8",
            capture_output=True,
        )
        trees[path] = result.stdout.strip() if result.returncode == 0 else None
    return {
        "timestamp_utc": now(),
        "head": git("rev-parse", "HEAD"),
        "branch": git("branch", "--show-current"),
        "skill_tree": git("rev-parse", "HEAD:skill"),
        "protected_tree_hashes": trees,
        "git_status": git("status", "--short"),
    }


def initialize() -> None:
    before = RUN / "source-provenance/integrity-before.json"
    if before.exists():
        raise SystemExit("Refusing to overwrite the initial integrity snapshot")
    write_json("source-provenance/integrity-before.json", protected_snapshot())
    write_json(
        "workspace-manifest.yaml",
        {
            "schema_version": 1,
            "benchmark_id": BENCHMARK_ID,
            "run_id": RUN_ID,
            "allowed_write_root": str(RUN),
            "allowed_read_roots": [str(REPO / "skill"), str(RUN)],
            "immutable_inputs": [],
            "status": "SOURCE_ACQUISITION",
            "excellent_solutions_accessed": False,
            "note": "JSON is valid YAML; protected history is read only.",
        },
    )
    print(json.dumps(protected_snapshot(), ensure_ascii=False, indent=2))


def download() -> None:
    listing = json.loads(request(DIRECTORY_API))
    compact = [
        {
            "name": item["name"],
            "sha": item["sha"],
            "size": item.get("size"),
            "type": item["type"],
            "html_url": item.get("html_url"),
            "download_url": item.get("download_url"),
        }
        for item in listing
    ]
    write_json("source-provenance/directory-listing.json", compact)
    matches = [item for item in listing if item["name"] == FILENAME]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one target, found {len(matches)}")
    target = matches[0]
    if target["sha"] != EXPECTED_BLOB:
        raise RuntimeError(f"Directory blob mismatch: {target['sha']}")
    data = request(target["download_url"])
    computed_blob = blob_sha(data)
    if computed_blob != EXPECTED_BLOB:
        raise RuntimeError(f"Downloaded blob mismatch: {computed_blob}")
    destination = RUN / "source-provenance" / "original" / FILENAME
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise RuntimeError("Refusing to overwrite preserved original")
    destination.write_bytes(data)
    record = {
        "benchmark_id": BENCHMARK_ID,
        "source_status": "USER_DESIGNATED_HISTORICAL_MIRROR",
        "official_origin_independently_verified": False,
        "source_tree_url": DIRECTORY_URL,
        "directory_api_url": DIRECTORY_API,
        "file_url": target["html_url"],
        "raw_url": target["download_url"],
        "blob_api_url": (
            "https://api.github.com/repos/zhanwen/MathModel/git/blobs/"
            + EXPECTED_BLOB
        ),
        "git_blob_sha_expected": EXPECTED_BLOB,
        "git_blob_sha_computed": computed_blob,
        "sha256": sha256(data),
        "bytes": len(data),
        "original_file": FILENAME,
        "retrieved_utc": now(),
        "scope": "Only the designated 2007 problem directory listing and exact 2007A DOC were requested.",
        "excellent_solutions_accessed": False,
    }
    write_json("source-provenance/source.json", record)
    manifest_path = RUN / "workspace-manifest.yaml"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["immutable_inputs"] = [
        {"path": str(destination), "sha256": record["sha256"]}
    ]
    manifest["status"] = "INPUT_AUDIT"
    write_json("workspace-manifest.yaml", manifest)
    print(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in {"init", "download"}:
        raise SystemExit("usage: bootstrap.py init|download")
    {"init": initialize, "download": download}[sys.argv[1]]()
