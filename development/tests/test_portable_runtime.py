from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest
import yaml

from development.tooling.export_runtime_bundle import export_runtime_bundle
from development.tooling.prepare_clean_room import (
    CleanRoomError, RUNTIME_SCRIPT_FILES, RUNTIME_SUPPORT_FILES,
    RUNTIME_TEMPLATE_FILES, hash_directory, sha256,
)
from development.tooling.runtime_backend import BACKEND_KINDS, backend_contract, export_workspace_outputs
from development.tooling.runtime_launch_adapter import preflight_launch, validate_function_call_pairs
from development.tooling.validate_runtime_bundle import (
    capture_immutable_snapshot, runtime_integrity_status, validate_immutable_snapshot,
    validate_runtime_bundle, validate_workspace_write_path,
)


PROJECT = Path(__file__).resolve().parents[2]


def tiny_repo(root: Path) -> tuple[Path, Path]:
    repo = root / "developer-repo"
    (repo / "skill/scripts").mkdir(parents=True)
    (repo / "skill/templates").mkdir(parents=True)
    (repo / "skill/SKILL.md").write_text("---\nname: tiny-runtime\nmetadata:\n  version: V2.8\n---\nRuntime fixture.\n", encoding="utf-8")
    (repo / "skill/routing.yaml").write_text("version: 1\nroutes: {}\n", encoding="utf-8")
    for name in RUNTIME_SCRIPT_FILES:
        (repo / "skill/scripts" / name).write_text(f"# runtime tool {name}\n", encoding="utf-8")
    raw = repo / "benchmarks/problems/tiny/raw"
    raw.mkdir(parents=True)
    artifacts = []
    for index, name in enumerate(("problem.docx", "attachment1.xlsx", "attachment2.xlsx", "attachment3.xlsx", "attachment4.xlsx"), 1):
        (raw / name).write_bytes(f"tiny-input-{index}".encode())
        artifacts.append({"id": f"ART-{index:03d}", "filename": name, "raw_path": f"raw/{name}", "sha256": sha256(raw / name)})
    source = raw.parent / "source.yaml"
    source.write_text(yaml.safe_dump({"benchmark_id": "tiny", "artifacts": artifacts}), encoding="utf-8")
    (source.parent / "user-turns.yaml").write_text("synthetic-export-provenance: true\n", encoding="utf-8")
    for relative in ("benchmarks/runs/run-001/evaluation.yaml", "expected.yaml", "ground-truth.yaml", "AGENTS.md"):
        path = repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("expected_route: developer-only\n", encoding="utf-8")
    return repo, source


@pytest.fixture
def exported(tmp_path: Path):
    repo, source = tiny_repo(tmp_path)
    result = export_runtime_bundle(repo, "tiny", "run-portable", tmp_path / "A", problem_source=source, make_zip=True)
    return repo, source, result


def test_export_uses_clean_room_policy_and_canonical_inputs(exported) -> None:
    repo, source, result = exported
    bundle = result.bundle_root
    assert validate_runtime_bundle(bundle) == []
    manifest = yaml.safe_load(result.manifest_path.read_text(encoding="utf-8"))
    assert manifest["skill_hash"] == hash_directory(repo / "skill")
    assert manifest["frozen_user_script_sha256"] == sha256(source.parent / "user-turns.yaml")
    assert manifest["developer_repository_required"] is False
    assert len(manifest["input_artifacts"]) == 5
    for item in manifest["input_artifacts"]:
        runtime = bundle / item["relative_path"]
        canonical = source.parent / "raw" / runtime.name
        assert sha256(runtime) == item["sha256"] == sha256(canonical)
        assert not os.path.samefile(runtime, canonical)
        assert "artifact_id" not in item
    assert {p.relative_to(bundle).as_posix() for p in (bundle / "workspace").rglob("*") if p.is_file()} == {
        "workspace/evidence/active-evidence-set.yaml", "workspace/workspace-manifest.yaml",
    }
    assert not any((bundle / name).exists() for name in ("benchmarks", "harness", "tests", "AGENTS.md"))
    launch = json.loads((bundle / "launch-preflight.json").read_text(encoding="utf-8"))
    assert launch["transport"]["preflight_status"] == "UNKNOWN"
    assert launch["turn1_allowed"] is False


def test_moved_bundle_validates_without_developer_repository(exported, tmp_path: Path) -> None:
    repo, _, result = exported
    moved = tmp_path / "B"
    result.bundle_root.rename(moved)
    hidden = repo.with_name("developer-repo.hidden")
    repo.rename(hidden)
    environment = dict(os.environ, PYTHONPATH="", PYTHONDONTWRITEBYTECODE="1")
    try:
        completed = subprocess.run(
            [sys.executable, "-B", str(moved / "scripts/validate_runtime_bundle.py"), str(moved)],
            cwd=tmp_path, env=environment, capture_output=True, text=True, timeout=30,
        )
        assert completed.returncode == 0, completed.stderr + completed.stdout
        assert completed.stdout.strip() == "RUNTIME_BUNDLE_VALID"
        assert not list(moved.rglob("__pycache__"))
        assert validate_runtime_bundle(moved) == []
        # The portable V2.7 CLI also resolves all imports locally. Unknown
        # transport must remain blocked without any model invocation.
        preflight = subprocess.run(
            [sys.executable, "-B", str(moved / "scripts/runtime_launch_adapter.py"),
             "--prepared-root", str(moved), "--actual-root", str(moved),
             "--run-id", "run-portable", "--attempt-id", "fixture-attempt"],
            cwd=tmp_path, env=environment, capture_output=True, text=True, timeout=30,
        )
        report = json.loads(preflight.stdout)
        assert preflight.returncode == 1
        assert report["binding"]["binding_status"] == "PASS"
        assert report["turn1_allowed"] is False
        assert report["model_invocation_count"] == 0
    finally:
        hidden.rename(repo)


@pytest.mark.parametrize("relative", ["skill/SKILL.md", "input/attachment3.xlsx", "skill/scripts/metrics.py"])
def test_missing_required_file_fails(exported, relative: str) -> None:
    bundle = exported[2].bundle_root
    (bundle / relative).unlink()
    assert validate_runtime_bundle(bundle)


def test_modified_input_fails_without_changing_canonical(exported) -> None:
    _, source, result = exported
    original = sha256(source.parent / "raw/attachment1.xlsx")
    (result.bundle_root / "input/attachment1.xlsx").write_bytes(b"changed")
    assert any("hash mismatch" in error for error in validate_runtime_bundle(result.bundle_root))
    assert sha256(source.parent / "raw/attachment1.xlsx") == original


@pytest.mark.parametrize("relative", [
    "workspace/expected.yaml", "workspace/run-003/metrics.json",
    "skill/AGENTS.md", "skill/expected.yaml", "skill/result.txt",
    "benchmarks/runs/evaluation.yaml",
])
def test_evaluator_and_prior_run_leakage_fails(exported, relative: str) -> None:
    bundle = exported[2].bundle_root
    leaked = bundle / relative
    leaked.parent.mkdir(parents=True, exist_ok=True)
    leaked.write_text("{}", encoding="utf-8")
    assert any("forbidden visibility" in error for error in validate_runtime_bundle(bundle, post_run=True))


@pytest.mark.parametrize("marker", ["expected_route", "known_failure", "evaluator_notes", "first_meaningful_failure", "model_behavior_p0", "rubric_score"])
def test_renamed_evaluator_content_is_rejected(exported, marker: str) -> None:
    bundle = exported[2].bundle_root
    (bundle / "workspace/facts.yaml").write_text(f"{marker}: leaked\n", encoding="utf-8")
    assert any("forbidden visibility" in error for error in validate_runtime_bundle(bundle, post_run=True))


def test_workspace_policy_and_stale_active_evidence(exported) -> None:
    bundle = exported[2].bundle_root
    assert validate_workspace_write_path(bundle, "workspace/outputs/metrics.json")
    for path in ("../escaped.json", "skill/new.md", "input/new.xlsx", "workspace/../../escape", "workspace", "C:/outside/file", "/outside/file"):
        assert not validate_workspace_write_path(bundle, path)
    active = bundle / "workspace/evidence/active-evidence-set.yaml"
    active.write_text("active_run_id: run-002\nactive_evidence_set: {}\n", encoding="utf-8")
    assert any("active evidence run_id" in error for error in validate_runtime_bundle(bundle))


def test_post_run_outputs_allowed_but_immutable_changes_fail(exported) -> None:
    bundle = exported[2].bundle_root
    snapshot = capture_immutable_snapshot(bundle)
    (bundle / "workspace/outputs/metrics.json").write_text("{}", encoding="utf-8")
    assert validate_runtime_bundle(bundle, post_run=True) == []
    assert validate_immutable_snapshot(bundle, snapshot) == []
    assert validate_runtime_bundle(bundle)  # A used workspace cannot start a fresh run.
    (bundle / "skill/SKILL.md").write_text("modified", encoding="utf-8")
    assert runtime_integrity_status(bundle, snapshot) == "RUNTIME_INTEGRITY_FAIL"


def test_manifest_rewrite_cannot_bypass_trusted_snapshot(exported) -> None:
    bundle = exported[2].bundle_root
    snapshot = capture_immutable_snapshot(bundle)
    manifest_path = bundle / "runtime-manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest["allowed_write_root"] = "../"
    manifest_path.write_text(yaml.safe_dump(manifest), encoding="utf-8")
    assert validate_runtime_bundle(bundle, expected_manifest_sha256=snapshot["manifest_sha256"])
    assert runtime_integrity_status(bundle, snapshot) == "RUNTIME_INTEGRITY_FAIL"


def test_zip_hash_and_unpacked_empty_directories(exported, tmp_path: Path) -> None:
    result = exported[2]
    assert result.zip_sha256_path.read_text(encoding="ascii").split()[0] == sha256(result.zip_path)
    with zipfile.ZipFile(result.zip_path) as archive:
        archive.extractall(tmp_path / "unpacked")
    unpacked = tmp_path / "unpacked/A"
    assert (unpacked / "workspace/code").is_dir()
    assert validate_runtime_bundle(unpacked) == []


def test_export_requires_frozen_script_and_preserves_existing_output(tmp_path: Path) -> None:
    repo, source = tiny_repo(tmp_path)
    script = source.parent / "user-turns.yaml"
    script.unlink()
    with pytest.raises(CleanRoomError, match="frozen"):
        export_runtime_bundle(repo, "tiny", "run-portable", tmp_path / "missing", problem_source=source)
    existing = tmp_path / "existing"
    existing.mkdir()
    (existing / "keep.txt").write_text("retain", encoding="utf-8")
    with pytest.raises(FileExistsError):
        export_runtime_bundle(repo, "tiny", "run-portable", existing, problem_source=source)
    assert (existing / "keep.txt").read_text(encoding="utf-8") == "retain"


def test_portable_binding_reuses_v27_gates(exported, tmp_path: Path) -> None:
    repo, _, result = exported
    bundle = result.bundle_root
    mirror = tmp_path / "managed-mirror"
    shutil.copytree(bundle, mirror)
    caps = {"provider": "fixture", "protocol": "fixture", "api_mode": "fixture", "continuation_mode": "standalone",
            "supports_function_call_output": True, "requires_call_id": True}
    for actual, mode in ((bundle, "DIRECT"), (mirror, "MANAGED_MIRROR")):
        report = preflight_launch(bundle, actual, run_id="run-portable", attempt_id="fixture-attempt",
                                  developer_repository=repo, transport_capabilities=caps)
        assert report["binding"]["binding_mode"] == mode
        assert report["turn1_allowed"] is True
        assert report["model_invocation_count"] == 0
    (mirror / "input/attachment4.xlsx").unlink()
    failed = preflight_launch(bundle, mirror, run_id="run-portable", attempt_id="fixture-attempt",
                              transport_capabilities=caps)
    assert failed["turn1_allowed"] is False
    assert failed["model_invocation_count"] == 0


def test_backend_kind_does_not_claim_sandbox_evidence() -> None:
    for kind in BACKEND_KINDS:
        assert backend_contract(kind)["filesystem_isolation_level"] == "UNKNOWN"
    with pytest.raises(ValueError):
        backend_contract("uncontrolled-desktop")


def test_null_call_ids_are_not_a_valid_pair() -> None:
    events = [{"type": "function_call", "call_id": None}, {"type": "function_call_output", "call_id": None}]
    assert validate_function_call_pairs(events)["status"] == "TRANSPORT_PROTOCOL_FAIL"


def test_output_export_requires_session_stop_and_preserves_frozen_transfer(exported, tmp_path: Path) -> None:
    bundle = exported[2].bundle_root
    snapshot = capture_immutable_snapshot(bundle)
    (bundle / "workspace/outputs/metrics.json").write_text("{}", encoding="utf-8")
    destination = tmp_path / "evaluator-transfer"
    with pytest.raises(ValueError, match="stop"):
        export_workspace_outputs(bundle, destination, snapshot=snapshot, session_stopped=False, execution_metadata={})
    assert not destination.exists()
    export_workspace_outputs(bundle, destination, snapshot=snapshot, session_stopped=True, execution_metadata={"session": "synthetic"})
    assert {path.name for path in destination.iterdir()} == {"workspace", "runtime-execution-metadata.json"}
    assert sha256(destination / "workspace/outputs/metrics.json") == sha256(bundle / "workspace/outputs/metrics.json")
    shutil.rmtree(bundle)
    assert (destination / "workspace/outputs/metrics.json").is_file()


def test_mutated_runtime_cannot_export_outputs(exported, tmp_path: Path) -> None:
    bundle = exported[2].bundle_root
    snapshot = capture_immutable_snapshot(bundle)
    (bundle / "skill/scripts/metrics.py").write_text("changed", encoding="utf-8")
    with pytest.raises(ValueError, match="RUNTIME_INTEGRITY_FAIL"):
        export_workspace_outputs(bundle, tmp_path / "rejected", snapshot=snapshot, session_stopped=True, execution_metadata={})


@pytest.mark.parametrize("mutation", ["invalid-yaml", "escape-path", "empty-input-list", "missing-policy-module"])
def test_validator_cli_fails_closed_with_single_status(exported, tmp_path: Path, mutation: str) -> None:
    result = exported[2]
    if mutation == "missing-policy-module":
        (result.bundle_root / "skill/scripts/metrics.py").unlink()
    elif mutation == "invalid-yaml":
        result.manifest_path.write_text("[", encoding="utf-8")
    else:
        manifest = yaml.safe_load(result.manifest_path.read_text(encoding="utf-8"))
        if mutation == "escape-path":
            manifest["files"][0]["relative_path"] = "../outside.txt"
        else:
            manifest["input_artifacts"] = []
        result.manifest_path.write_text(yaml.safe_dump(manifest), encoding="utf-8")
    completed = subprocess.run([sys.executable, "-B", str(PROJECT / "development/tooling/validate_runtime_bundle.py"), str(result.bundle_root)],
                               cwd=tmp_path, capture_output=True, text=True, timeout=30)
    assert completed.returncode == 1
    assert completed.stdout.strip() == "RUNTIME_BUNDLE_INVALID"
    assert not completed.stderr
