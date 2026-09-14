from __future__ import annotations

import hashlib
import shutil
from types import SimpleNamespace
from pathlib import Path

import yaml

from development.tooling.prepare_clean_room import RUNTIME_SCRIPT_FILES, RUNTIME_SUPPORT_FILES, RUNTIME_TEMPLATE_FILES, prepare_clean_room
from development.tooling.runtime_launch_adapter import (
    preflight_launch,
    transport_preflight,
    validate_function_call_pairs,
    verify_runtime_binding,
    RuntimeLaunchAdapter,
)


CAPABILITIES = {
    "provider": "test-provider",
    "protocol": "responses",
    "api_mode": "http",
    "continuation_mode": "standalone",
    "supports_function_call_output": True,
    "requires_call_id": True,
}


def fake_prepared_room(tmp_path: Path) -> tuple[Path, Path]:
    repo = tmp_path / "developer-repo"
    (repo / "skill/references").mkdir(parents=True)
    (repo / "templates").mkdir()
    (repo / "scripts").mkdir()
    (repo / "problem/raw").mkdir(parents=True)
    (repo / "skill/SKILL.md").write_text("runtime skill", encoding="utf-8")
    (repo / "skill/references/runtime.md").write_text("runtime reference", encoding="utf-8")
    for name in RUNTIME_TEMPLATE_FILES:
        (repo / "templates" / name).write_text(f"template {name}", encoding="utf-8")
    for name in RUNTIME_SCRIPT_FILES:
        (repo / "scripts" / name).write_text(f"# script {name}\n", encoding="utf-8")
    for relative in RUNTIME_SUPPORT_FILES:
        (repo / relative).parent.mkdir(parents=True, exist_ok=True)
        (repo / relative).write_text("runtime compliance reference", encoding="utf-8")
    artifacts = []
    for index, name in enumerate(("problem.docx", "attachment1.xlsx", "attachment2.xlsx", "attachment3.xlsx", "attachment4.xlsx"), 1):
        content = f"artifact-{index}".encode()
        source = repo / "problem/raw" / name
        source.write_bytes(content)
        artifacts.append({"id": f"ART-{index:03d}", "filename": name, "raw_path": f"raw/{name}", "sha256": hashlib.sha256(content).hexdigest()})
    source_record = repo / "problem/source.yaml"
    source_record.write_text(yaml.safe_dump({"artifacts": artifacts}, sort_keys=False), encoding="utf-8")
    result = prepare_clean_room(repo, "tiny", "run-adapter", source_record, output_root=tmp_path / "prepared")
    return result.root, repo


def mirror(prepared: Path, target: Path) -> Path:
    shutil.copytree(prepared, target)
    return target


def test_direct_and_managed_mirror_bindings_pass(tmp_path: Path) -> None:
    prepared, repo = fake_prepared_room(tmp_path)
    direct = verify_runtime_binding(prepared, prepared, run_id="run-adapter", attempt_id="attempt-001", developer_repository=repo)
    assert direct["binding_mode"] == "DIRECT"
    assert direct["binding_status"] == "PASS"
    managed = mirror(prepared, tmp_path / "managed-session")
    report = verify_runtime_binding(prepared, managed, run_id="run-adapter", attempt_id="attempt-002", developer_repository=repo)
    assert report["binding_mode"] == "MANAGED_MIRROR"
    assert report["binding_status"] == "PASS"
    assert report["filesystem_isolation_level"] == "PROJECT_ROOT_VERIFIED"
    assert all(item["status"] == "PASS" for item in report["required_runtime_paths"])


def test_empty_mirror_missing_skill_and_input_fail(tmp_path: Path) -> None:
    prepared, repo = fake_prepared_room(tmp_path)
    empty = tmp_path / "empty-session"
    (empty / "outputs").mkdir(parents=True)
    (empty / "work").mkdir()
    empty_report = verify_runtime_binding(prepared, empty, run_id="run-adapter", attempt_id="attempt-empty", developer_repository=repo)
    assert empty_report["binding_status"] == "FAIL"
    assert empty_report["missing_runtime_paths"]

    no_skill = mirror(prepared, tmp_path / "no-skill")
    (no_skill / "skill/SKILL.md").unlink()
    assert verify_runtime_binding(prepared, no_skill, run_id="run-adapter", attempt_id="attempt-skill", developer_repository=repo)["binding_status"] == "FAIL"

    no_input = mirror(prepared, tmp_path / "no-input")
    (no_input / "input/attachment3.xlsx").unlink()
    assert verify_runtime_binding(prepared, no_input, run_id="run-adapter", attempt_id="attempt-input", developer_repository=repo)["binding_status"] == "FAIL"


def test_actual_root_forbidden_artifact_and_hash_mismatch_fail(tmp_path: Path) -> None:
    prepared, repo = fake_prepared_room(tmp_path)
    forbidden = mirror(prepared, tmp_path / "forbidden")
    (forbidden / "evaluation.yaml").write_text("score: 0", encoding="utf-8")
    report = verify_runtime_binding(prepared, forbidden, run_id="run-adapter", attempt_id="attempt-forbidden", developer_repository=repo)
    assert report["binding_status"] == "FAIL"
    assert report["forbidden_matches"]

    mismatch = mirror(prepared, tmp_path / "mismatch")
    (mismatch / "skill/SKILL.md").write_text("tampered", encoding="utf-8")
    mismatch_report = verify_runtime_binding(prepared, mismatch, run_id="run-adapter", attempt_id="attempt-mismatch", developer_repository=repo)
    assert mismatch_report["binding_status"] == "FAIL"
    assert "skill/SKILL.md" in mismatch_report["hash_mismatches"]

    prior = mirror(prepared, tmp_path / "prior-run")
    (prior / "run-002").mkdir()
    prior_report = verify_runtime_binding(prepared, prior, run_id="run-adapter", attempt_id="attempt-prior", developer_repository=repo)
    assert prior_report["binding_status"] == "FAIL"
    assert prior_report["prior_runs_visible"] is True


def test_developer_repository_root_is_rejected(tmp_path: Path) -> None:
    prepared, repo = fake_prepared_room(tmp_path)
    actual = repo / "model-root"
    mirror(prepared, actual)
    report = verify_runtime_binding(prepared, actual, run_id="run-adapter", attempt_id="attempt-repo", developer_repository=repo)
    assert report["binding_status"] == "FAIL"
    assert report["developer_repository_visible"] is True


def test_transport_pairing_and_orphans() -> None:
    valid = [{"type": "function_call", "call_id": "call_123"}, {"type": "function_call_output", "call_id": "call_123"}]
    assert validate_function_call_pairs(valid)["status"] == "PASS"
    assert validate_function_call_pairs([{"type": "function_call_output"}])["status"] == "TRANSPORT_PROTOCOL_FAIL"
    assert validate_function_call_pairs([{"type": "function_call", "call_id": "call_123"}, {"type": "function_call_output", "call_id": "call_456"}])["status"] == "TRANSPORT_PROTOCOL_FAIL"


def test_transport_capability_unknown_and_orphan_fail() -> None:
    assert transport_preflight(None)["preflight_status"] == "UNKNOWN"
    report = transport_preflight(CAPABILITIES, [{"type": "function_call_output", "call_id": "orphan"}])
    assert report["preflight_status"] == "TRANSPORT_PROTOCOL_FAIL"
    assert report["pairing"]["errors"]


def test_adapter_launch_requires_platform_session_and_never_invokes_model(tmp_path: Path, monkeypatch) -> None:
    prepared, repo = fake_prepared_room(tmp_path)
    adapter = RuntimeLaunchAdapter(repo)
    monkeypatch.setattr(adapter, "prepare", lambda *args, **kwargs: SimpleNamespace(root=prepared))
    blocked = adapter.launch("tiny", "run-adapter", "ignored", attempt_id="attempt-no-session")
    assert blocked["launch_status"] == "BLOCKED_BY_PLATFORM"
    assert blocked["turn1_allowed"] is False
    assert blocked["model_invocation_count"] == 0

    managed = mirror(prepared, tmp_path / "launch-mirror")
    ready = adapter.launch(
        "tiny",
        "run-adapter",
        "ignored",
        attempt_id="attempt-session",
        session_factory=lambda _prepared: managed,
        transport_capabilities=CAPABILITIES,
    )
    assert ready["launch_status"] == "READY_FOR_MODEL_TURN_1"
    assert ready["turn1_allowed"] is True


def test_failed_preflight_never_allows_model_turn(tmp_path: Path) -> None:
    prepared, repo = fake_prepared_room(tmp_path)
    result = preflight_launch(
        prepared,
        tmp_path / "empty-session",
        run_id="run-adapter",
        attempt_id="attempt-gated",
        transport_capabilities=CAPABILITIES,
        transport_events=[{"type": "function_call_output", "call_id": "orphan"}],
        developer_repository=repo,
    )
    assert result["turn1_allowed"] is False
    assert result["model_invocation_count"] == 0
    assert result["startup_state"][-1] == "ABORT_BEFORE_TURN_1"
