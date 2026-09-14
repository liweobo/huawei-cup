from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path

import pytest
import yaml

from development.tooling.prepare_clean_room import (
    CleanRoomError,
    RUNTIME_SCRIPT_FILES,
    RUNTIME_SUPPORT_FILES,
    canonicalize_clean_room,
    prepare_clean_room,
    scan_visibility,
    sha256,
    validate_generated_path,
)
from skill.scripts.runtime_provenance import validate_workspace_manifest


TEMPLATES = (
    "active-evidence-set.yaml",
    "active-files.yaml",
    "competition-state.md",
    "experiment-record.md",
    "experiment-record.yaml",
    "handoff.md",
    "paper-claim.yaml",
    "reviewer-report.md",
    "source-record.md",
    "task-anchor.md",
    "workspace-manifest.yaml",
)
SCRIPTS = (
    "__init__.py",
    "data_audit.py",
    "metrics.py",
    "plotting.py",
    "robustness.py",
    "runtime_provenance.py",
    "sensitivity.py",
)


def fake_repo(tmp_path: Path) -> tuple[Path, Path, dict[str, str]]:
    repo = tmp_path / "developer-repo"
    (repo / "skill/references").mkdir(parents=True)
    (repo / "templates").mkdir()
    (repo / "scripts").mkdir()
    (repo / "problem/raw").mkdir(parents=True)
    (repo / "skill/SKILL.md").write_text("runtime skill V2.6", encoding="utf-8")
    (repo / "skill/references/runtime.md").write_text("runtime reference", encoding="utf-8")
    for name in TEMPLATES:
        (repo / "templates" / name).write_text(f"runtime template {name}", encoding="utf-8")
    for name in RUNTIME_SCRIPT_FILES:
        (repo / "scripts" / name).write_text(f"# runtime tool {name}\n", encoding="utf-8")
    for relative in RUNTIME_SUPPORT_FILES:
        (repo / relative).parent.mkdir(parents=True, exist_ok=True)
        (repo / relative).write_text("runtime compliance reference", encoding="utf-8")
    # Evaluator/developer assets must remain outside the model-visible bundle.
    (repo / "benchmarks/runs/run-001").mkdir(parents=True)
    (repo / "benchmarks/runs/run-001/evaluation.yaml").write_text("score: 0", encoding="utf-8")
    for name in ("expected.yaml", "ground-truth.yaml", "problem-facts.yaml", "postmortem.md", "AGENTS.md"):
        (repo / name).write_text("expected_route: forbidden", encoding="utf-8")

    contents = {
        "problem.docx": b"problem",
        "attachment1.xlsx": b"train-data",
        "attachment2.xlsx": b"test-waveform",
        "attachment3.xlsx": b"test-loss",
        "attachment4.xlsx": b"answer-template",
    }
    artifacts = []
    for index, (name, data) in enumerate(contents.items(), start=1):
        path = repo / "problem/raw" / name
        path.write_bytes(data)
        artifacts.append({
            "id": f"ART-{index:03d}",
            "filename": name,
            "raw_path": f"raw/{name}",
            "sha256": hashlib.sha256(data).hexdigest(),
        })
    source = repo / "problem/source.yaml"
    source.write_text(yaml.safe_dump({"artifacts": artifacts}, sort_keys=False), encoding="utf-8")
    return repo, source, {item["id"]: item["sha256"] for item in artifacts}


def test_prepare_clean_room_excludes_developer_and_evaluator_assets(tmp_path: Path) -> None:
    repo, source, hashes = fake_repo(tmp_path)
    result = prepare_clean_room(repo, "tiny-benchmark", "run-test", source, output_root=tmp_path / "room")
    report = yaml.safe_load(result.visibility_report_path.read_text(encoding="utf-8"))
    manifest = yaml.safe_load(result.manifest_path.read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["forbidden_matches"] == []
    assert manifest["developer_repository_visible"] is False
    assert manifest["prior_runs_visible"] is False
    assert manifest["evaluator_files_visible"] is False
    assert manifest["writable_root"] == "workspace"
    assert len(manifest["input_artifacts"]) == 5
    assert {item["canonical_sha256"] for item in manifest["input_artifacts"]} == set(hashes.values())
    assert not (result.root / "benchmarks").exists()
    assert not (result.root / "expected.yaml").exists()
    assert not (result.root / "AGENTS.md").exists()
    assert (result.root / "skill/SKILL.md").is_file()
    assert (result.root / "workspace/evidence/active-evidence-set.yaml").is_file()
    workspace_manifest = yaml.safe_load((result.root / "workspace/workspace-manifest.yaml").read_text(encoding="utf-8"))
    assert not validate_workspace_manifest(workspace_manifest)


def test_clean_room_rejects_content_marker_and_previous_run_output(tmp_path: Path) -> None:
    repo, source, _ = fake_repo(tmp_path)
    (repo / "skill/leak.yaml").write_text("expected_route: leaked", encoding="utf-8")
    with pytest.raises(CleanRoomError, match="visibility scan failed"):
        prepare_clean_room(repo, "tiny-benchmark", "run-marker", source, output_root=tmp_path / "marker-room")
    (repo / "skill/leak.yaml").unlink()

    result = prepare_clean_room(repo, "tiny-benchmark", "run-visible", source, output_root=tmp_path / "visible-room")
    leaked = result.root / "workspace/run-002/metrics.json"
    leaked.parent.mkdir()
    leaked.write_text("{\"accuracy\": 1}", encoding="utf-8")
    report = scan_visibility(result.root, "run-visible")
    assert report["status"] == "CLEAN_ROOM_FAIL"
    assert any("run-002" in item for item in report["forbidden_matches"])
    leaked.unlink()
    renamed = result.root / "workspace/facts.yaml"
    renamed.write_text("known_failure: hidden", encoding="utf-8")
    report = scan_visibility(result.root, "run-visible")
    assert report["status"] == "CLEAN_ROOM_FAIL"
    assert any("facts.yaml" in item for item in report["content_leakage_matches"])


def test_clean_room_rejects_source_hash_mismatch(tmp_path: Path) -> None:
    repo, source, _ = fake_repo(tmp_path)
    data = yaml.safe_load(source.read_text(encoding="utf-8"))
    data["artifacts"][0]["sha256"] = "0" * 64
    source.write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(CleanRoomError, match="hash mismatch"):
        prepare_clean_room(repo, "tiny-benchmark", "run-bad-hash", source, output_root=tmp_path / "bad-room")


def test_writable_root_and_canonicalization(tmp_path: Path) -> None:
    repo, source, _ = fake_repo(tmp_path)
    result = prepare_clean_room(repo, "tiny-benchmark", "run-canon", source, output_root=tmp_path / "canon-room", use_hardlinks=False)
    workspace = result.root / "workspace"
    output = workspace / "outputs/metrics.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("{\"rmse\": 0.1}", encoding="utf-8")
    assert validate_generated_path(output, workspace)
    assert not validate_generated_path(result.root / "outside.txt", workspace)
    archive = canonicalize_clean_room(result.root, tmp_path / "archive", paths=["clean-room-manifest.yaml", "workspace"], remove=True)
    assert not result.root.exists()
    assert (archive / "workspace/outputs/metrics.json").is_file()
    assert sha256(archive / "workspace/outputs/metrics.json") == hashlib.sha256(b'{"rmse": 0.1}').hexdigest()
    canonicalization = yaml.safe_load((archive / "canonicalization-manifest.yaml").read_text(encoding="utf-8"))
    assert canonicalization["clean_room_removed"] is True
    assert any(item["path"] == "workspace/outputs/metrics.json" for item in canonicalization["artifacts"])


def test_default_clean_room_is_under_system_temp_and_runtime_files_are_copies(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo, source, _ = fake_repo(tmp_path)
    system_temp = tmp_path / "system-temp"
    monkeypatch.setattr(tempfile, "gettempdir", lambda: str(system_temp))
    result = prepare_clean_room(repo, "tiny-benchmark", "run-default", source, use_hardlinks=True)
    try:
        assert result.root == system_temp / "huawei-cup-benchmark/run-default"
        assert not result.root.is_relative_to(repo)
        assert result.root.joinpath("skill/SKILL.md").stat().st_ino != repo.joinpath("skill/SKILL.md").stat().st_ino
    finally:
        import shutil
        shutil.rmtree(result.root, ignore_errors=True)
