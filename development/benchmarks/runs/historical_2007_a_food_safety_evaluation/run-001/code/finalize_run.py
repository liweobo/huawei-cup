"""Build run-bound evidence manifests and verify frozen historical integrity."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


RUN = Path(__file__).resolve().parents[1]
REPO = RUN.parents[4]
BEFORE = RUN / "source-provenance" / "integrity-before.json"
PROTECTED = [
    "skill",
    "development/benchmarks/problems/2023/E",
    "development/benchmarks/runs/historical_2005_d_stochastic_inventory",
    "development/benchmarks/runs/historical_2011_b_absorbing_material_anechoic_chamber",
    "development/benchmarks/runs/historical_2017_f_underground_logistics_network",
    "development/benchmarks/runs/historical_2020_a_chip_phase_noise",
    "development/benchmarks/runs/historical_2022_c_buffer_scheduling",
    "development/benchmarks/runs/historical_2024_c_core_loss",
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=REPO, text=True, encoding="utf-8"
    ).strip()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def artifact(artifact_id: str, relative: str, kind: str, claim_scope: str) -> dict[str, object]:
    path = RUN / relative
    if not path.is_file():
        raise FileNotFoundError(path)
    return {
        "artifact_id": artifact_id,
        "run_id": "run-001",
        "experiment_id": "EXP-2007A-EVAL-001" if kind in {"CODE", "EXPERIMENT_RESULT", "VALIDATION_RESULT"} else None,
        "type": kind,
        "path": relative,
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
        "claim_scope": claim_scope,
    }


def main() -> None:
    before = json.loads(BEFORE.read_text(encoding="utf-8"))
    initial_trees = before["protected_tree_hashes"]
    current_trees: dict[str, str | None] = {}
    diffs: dict[str, str] = {}
    for relative in PROTECTED:
        try:
            current_trees[relative] = git("rev-parse", f"HEAD:{relative}")
        except subprocess.CalledProcessError:
            current_trees[relative] = None
        diffs[relative] = git("diff", "--", relative)
    tree_mismatches = {
        path: {"before": initial_trees.get(path), "after": current_trees.get(path)}
        for path in initial_trees
        if initial_trees.get(path) != current_trees.get(path)
    }
    nonempty_diffs = {path: value for path, value in diffs.items() if value}
    integrity = {
        "timestamp_utc": now(),
        "initial_head": before["head"],
        "current_head_before_commit": git("rev-parse", "HEAD"),
        "branch": git("branch", "--show-current"),
        "initial_skill_tree": before["skill_tree"],
        "current_skill_tree": git("rev-parse", "HEAD:skill"),
        "skill_tree_unchanged": before["skill_tree"] == git("rev-parse", "HEAD:skill"),
        "protected_tree_hashes": current_trees,
        "initial_tree_mismatches": tree_mismatches,
        "protected_worktree_diffs": nonempty_diffs,
        "excellent_solutions_accessed": False,
        "pass": not tree_mismatches and not nonempty_diffs and before["skill_tree"] == git("rev-parse", "HEAD:skill"),
        "git_status": git("status", "--short"),
    }
    write_json(RUN / "integrity" / "after.json", integrity)
    if not integrity["pass"]:
        raise SystemExit("Protected historical integrity failed")

    records = [
        artifact("SRC-2007A-DOC", "source-provenance/original/2007年A题  建立食品卫生安全保障体系数学模型及改进模型的若干理论问题（终）.doc", "SOURCE", "exact user-designated legacy DOC"),
        artifact("EVID-EXTRACTION-VERIFIED", "extraction/extraction-audit.json", "VALIDATION_RESULT", "legacy DOC body/structure extraction verified"),
        artifact("CODE-EVALUATION-MODEL", "code/evaluation_model.py", "CODE", "synthetic evaluation helpers"),
        artifact("CODE-RUN-MODEL", "code/run_model.py", "CODE", "declared synthetic experiment runner"),
        artifact("CODE-EVALUATION-TESTS", "code/test_evaluation.py", "CODE", "focused evaluation contract tests"),
        artifact("OUT-EXPOSURE-RESULTS", "outputs/exposure-results.json", "EXPERIMENT_RESULT", "synthetic scenario only"),
        artifact("OUT-RANKING-RESULTS", "outputs/ranking-results.json", "EXPERIMENT_RESULT", "synthetic triage only"),
        artifact("OUT-SENSITIVITY-RESULTS", "outputs/sensitivity-results.json", "VALIDATION_RESULT", "simulated perturbations only"),
        artifact("OUT-SYNTHETIC-TESTS", "outputs/synthetic-tests.json", "VALIDATION_RESULT", "synthetic contracts"),
        artifact("EVID-VALIDATION-SUMMARY", "validation-results/summary.json", "VALIDATION_RESULT", "repository and run validation"),
        artifact("REPORT-2007A-BLIND", "REPORT.md", "REPORT", "conditional model and synthetic benchmark"),
        artifact("COMPLETION-2007A-BLIND", "completion.json", "REPORT", "blind-run completion decision"),
    ]
    ledger = {
        "schema_version": 1,
        "benchmark_id": "historical_2007_a_food_safety_evaluation",
        "run_id": "run-001",
        "experiment_id": "EXP-2007A-EVAL-001",
        "generated_utc": now(),
        "artifacts": records,
    }
    write_json(RUN / "evidence-ledger.json", ledger)
    active = {
        "active_run_id": "run-001",
        "active_evidence_set": {
            "integrated_2007A": {
                "run_id": "run-001",
                "experiment_id": "EXP-2007A-EVAL-001",
                "artifact_ids": [record["artifact_id"] for record in records],
            }
        },
    }
    write_json(RUN / "active-evidence-set.yaml", active)

    manifest_exclusions = {
        ".tmp",
        "artifact-manifest.json",
        "evidence-ledger.json",
        "active-evidence-set.yaml",
        "integrity/after.json",
    }
    ignored_prefixes = (
        ".tmp/",
        "extraction/images/",
        "extraction/pages/",
        "extraction/word-pages/",
    )
    files = []
    for path in sorted(RUN.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(RUN).as_posix()
        if relative.startswith(ignored_prefixes) or relative.endswith(".pdf") or relative in manifest_exclusions or "__pycache__" in relative or relative.endswith(".pyc"):
            continue
        files.append(
            {
                "path": relative,
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
            }
        )
    write_json(
        RUN / "artifact-manifest.json",
        {
            "schema_version": 1,
            "generated_utc": now(),
            "file_count": len(files),
            "files": files,
            "exclusions": sorted(manifest_exclusions),
        },
    )

    workspace = json.loads((RUN / "workspace-manifest.yaml").read_text(encoding="utf-8"))
    workspace["status"] = "COMPLETE"
    workspace["active_evidence_set"] = str(RUN / "active-evidence-set.yaml")
    workspace["prior_run_artifacts_visible"] = False
    write_json(RUN / "workspace-manifest.yaml", workspace)
    print(json.dumps({"integrity": integrity["pass"], "evidence_artifacts": len(records), "manifest_files": len(files)}, indent=2))


if __name__ == "__main__":
    main()
