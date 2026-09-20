"""Recompute post-run integrity snapshots for source, Skill and historical assets."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
RUN = Path(__file__).resolve().parents[1]
OUT = RUN / "validation"


def git(*args):
    return subprocess.run(
        ["git", "-C", str(ROOT), *args],
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


doc = RUN / "source-provenance" / "仓库容量有限条件下的随机存贮模型（D）.doc"
source_after = {
    "file": doc.name,
    "sha256_after": sha256(doc),
    "size_bytes_after": doc.stat().st_size,
    "expected_git_blob_sha": "cc7540cbfa71e42d5a8809e933a3856e3c924197",
    "source_files_present": sorted(
        p.name for p in (RUN / "source-provenance").iterdir() if p.suffix == ".doc"
    ),
}
(OUT / "source-integrity-after.json").write_text(
    json.dumps(source_after, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
)

skill_after = {
    "skill_tree_hash_after": git("rev-parse", "HEAD:skill"),
    "skill_worktree_diff": git("status", "--porcelain", "--", "skill"),
    "skill_modified": bool(git("status", "--porcelain", "--", "skill")),
}
(OUT / "skill-integrity-after.json").write_text(
    json.dumps(skill_after, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
)

protected = [
    "development/benchmarks/runs/historical_2020_a_chip_phase_noise/run-001",
    "development/benchmarks/runs/historical_2011_b_absorbing_material_anechoic_chamber",
    "development/benchmarks/runs/historical_2022_c_buffer_scheduling/run-001",
    "development/benchmarks/runs/historical_2022_c_buffer_scheduling/run-002",
    "development/benchmarks/runs/historical_2024_c_core_loss",
]
historical_after = {
    "protected_paths": {},
    "tracked_diff_in_protected_paths": git(
        "status", "--porcelain", "--", *protected
    ),
}
for path in protected:
    HEAD = git("rev-parse", f"HEAD:{path}")
    historical_after["protected_paths"][path] = {
        "head_tree_present": bool(HEAD),
        "worktree_modified_tracked": bool(
            git("status", "--porcelain", "--", path)
        ),
    }
historical_after["frozen_assets_unmodified"] = not historical_after[
    "tracked_diff_in_protected_paths"
]
(OUT / "historical-integrity-after.json").write_text(
    json.dumps(historical_after, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
)

print(json.dumps(source_after, indent=2, ensure_ascii=False))
print(json.dumps(skill_after, indent=2, ensure_ascii=False))
print(json.dumps(historical_after, indent=2, ensure_ascii=False))
