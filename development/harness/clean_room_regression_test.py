"""Regression checks for the clean-room runtime boundary."""

from __future__ import annotations

import hashlib
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from development.tooling.prepare_clean_room import (
    CleanRoomError,
    RUNTIME_SCRIPT_FILES,
    RUNTIME_SUPPORT_FILES,
    RUNTIME_TEMPLATE_FILES,
    canonicalize_clean_room,
    prepare_clean_room,
    scan_visibility,
    validate_generated_path,
)


def check(label: str, ok: bool, failures: list[str]) -> None:
    print(f"{'PASS' if ok else 'FAIL'} | {label}")
    if not ok:
        failures.append(label)


def fixture(root: Path) -> tuple[Path, Path, str]:
    repo = root / "developer-repo"
    (repo / "skill/references").mkdir(parents=True)
    (repo / "templates").mkdir()
    (repo / "scripts").mkdir()
    (repo / "problem/raw").mkdir(parents=True)
    (repo / "skill/SKILL.md").write_text("runtime skill", encoding="utf-8")
    for name in RUNTIME_TEMPLATE_FILES:
        (repo / "templates" / name).write_text("runtime template", encoding="utf-8")
    for name in RUNTIME_SCRIPT_FILES:
        (repo / "scripts" / name).write_text("# runtime tool\n", encoding="utf-8")
    for relative in RUNTIME_SUPPORT_FILES:
        (repo / relative).parent.mkdir(parents=True, exist_ok=True)
        (repo / relative).write_text("runtime compliance reference", encoding="utf-8")
    for name, content in {
        "problem.docx": b"problem",
        "attachment1.xlsx": b"training",
        "attachment2.xlsx": b"waveform",
    }.items():
        (repo / "problem/raw" / name).write_bytes(content)
    artifacts = []
    for index, name in enumerate(("problem.docx", "attachment1.xlsx", "attachment2.xlsx"), start=1):
        data = (repo / "problem/raw" / name).read_bytes()
        artifacts.append({"id": f"ART-{index:03d}", "filename": name, "raw_path": f"raw/{name}", "sha256": hashlib.sha256(data).hexdigest()})
    source = repo / "problem/source.yaml"
    source.write_text(yaml.safe_dump({"artifacts": artifacts}), encoding="utf-8")
    # These are intentionally in the developer repository only.
    (repo / "benchmarks/runs/run-001").mkdir(parents=True)
    (repo / "benchmarks/runs/run-001/evaluation.yaml").write_text("score: 1", encoding="utf-8")
    (repo / "expected.yaml").write_text("expected_route: forbidden", encoding="utf-8")
    return repo, source, artifacts[0]["sha256"]


def main() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="huawei-cup-clean-room-") as temp:
        root = Path(temp)
        repo, source, first_hash = fixture(root)
        result = prepare_clean_room(repo, "tiny", "run-clean", source, output_root=root / "room", skill_version="V2.6")
        manifest = yaml.safe_load(result.manifest_path.read_text(encoding="utf-8"))
        report = yaml.safe_load(result.visibility_report_path.read_text(encoding="utf-8"))
        visible = set(report["visible_paths"])
        check("prior run paths are excluded", not any("run-001" in path or "run-002" in path or "run-003" in path for path in visible), failures)
        check("evaluator files are excluded", not any(Path(path).name in {"evaluation.yaml", "expected.yaml", "ground-truth.yaml", "problem-facts.yaml", "postmortem.md"} for path in visible), failures)
        check("raw input hash matches canonical source", manifest["input_artifacts"][0]["canonical_sha256"] == first_hash == manifest["input_artifacts"][0]["runtime_sha256"], failures)
        check("runtime skill identity is hash-verifiable", bool(manifest.get("skill_hash")) and len(manifest["skill_hash"]) == 64, failures)
        check("pre-run visibility report passes", report["status"] == "PASS" and not report["forbidden_matches"], failures)
        workspace = result.root / "workspace"
        generated = workspace / "outputs/result.json"
        generated.parent.mkdir(parents=True, exist_ok=True)
        generated.write_text("{}", encoding="utf-8")
        check("generated path inside workspace is accepted", validate_generated_path(generated, workspace), failures)
        check("developer repository path is rejected for writes", not validate_generated_path(repo / "result.json", workspace), failures)
        leaked = workspace / "run-002/metrics.json"
        leaked.parent.mkdir()
        leaked.write_text("{}", encoding="utf-8")
        check("previous run output is rejected by visibility gate", scan_visibility(result.root, "run-clean")["status"] == "CLEAN_ROOM_FAIL", failures)
        leaked.unlink()
        active = yaml.safe_load((result.root / "workspace/evidence/active-evidence-set.yaml").read_text(encoding="utf-8"))
        check("active evidence set is bound to current run", active["active_run_id"] == "run-clean", failures)
        archive = canonicalize_clean_room(result.root, root / "archive", paths=["clean-room-manifest.yaml", "workspace"], remove=True)
        check("canonicalization preserves selected output", (archive / "workspace/outputs/result.json").is_file(), failures)
        check("clean room can be removed after canonicalization", not result.root.exists(), failures)
        check("canonicalization manifest is retained", (archive / "canonicalization-manifest.yaml").is_file(), failures)

    print(f"\nClean-room Regression Test: {'PASS' if not failures else 'FAIL'} ({13 - len(failures)}/13 checks)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
