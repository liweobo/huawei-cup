"""Acquire only the five allowlisted 2021D source blobs from GitHub.

The script deliberately addresses immutable Git blob IDs. It does not list or
clone the upstream repository, so forbidden excellent-paper paths are never
requested.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen


RUN_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = RUN_ROOT / "source-provenance" / "original"
RAW_ROOT = "https://raw.githubusercontent.com/zhanwen/MathModel/master"
UPSTREAM_DIR = "国赛试题/2021年研究生数学建模竞赛试题/D"
# Direct GitHub TLS was unavailable in the execution environment. This mirror
# transports the canonical raw URL; immutable Git blob verification remains
# the authority for every downloaded byte sequence.
TRANSPORT_PREFIX = "https://gh-proxy.com/"

SOURCES = [
    ("抗胰腺癌候选药物的优化建模.docx", "b970fb60d85c0dd650d1152463cabbabf3cfe619"),
    ("ERα_activity.xlsx", "a8cbbe3620d7794d475cf85b2351f6dba2a931e3"),
    ("ADMET.xlsx", "08cee79e5e3beffe574e327b877c6028add92dc6"),
    ("Molecular_Descriptor.xlsx", "21ee480d930e3befc65e55bdb283a01294a48bde"),
    ("分子描述符含义解释.xlsx", "29e813b8da02985a8043e1cee03120e65378cbd8"),
]


def git_blob_id(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    records = []
    for filename, expected_blob in SOURCES:
        canonical_url = f"{RAW_ROOT}/{quote(f'{UPSTREAM_DIR}/{filename}')}"
        transport_url = f"{TRANSPORT_PREFIX}{canonical_url}"
        request = Request(transport_url, headers={"User-Agent": "huawei-cup-blind-run"})
        with urlopen(request, timeout=60) as response:
            data = response.read()
        actual_blob = git_blob_id(data)
        if actual_blob != expected_blob:
            raise RuntimeError(f"blob mismatch for {filename}: {actual_blob}")
        destination = OUTPUT_DIR / filename
        destination.write_bytes(data)
        records.append(
            {
                "filename": filename,
                "canonical_source": canonical_url,
                "transport_url": transport_url,
                "expected_git_blob": expected_blob,
                "actual_git_blob": actual_blob,
                "sha256": hashlib.sha256(data).hexdigest(),
                "size_bytes": len(data),
                "verification": "PASS",
            }
        )
    manifest = {
        "benchmark_id": "historical_2021_d_candidate_drug_optimization",
        "retrieval_method": "canonical GitHub raw URL transported by gh-proxy.com; immutable Git blob verification",
        "allowlist_only": True,
        "forbidden_reference_paths_accessed": False,
        "files": records,
    }
    (RUN_ROOT / "source-provenance" / "source-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
