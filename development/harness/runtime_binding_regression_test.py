"""Deterministic V2.7 runtime binding and transport preflight regression."""

from __future__ import annotations

import hashlib
import shutil
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from development.tooling.prepare_clean_room import RUNTIME_SCRIPT_FILES, RUNTIME_SUPPORT_FILES, RUNTIME_TEMPLATE_FILES, prepare_clean_room
from development.tooling.runtime_launch_adapter import (
    preflight_launch,
    transport_preflight,
    validate_function_call_pairs,
    verify_runtime_binding,
)


CAPABILITIES = {
    "provider": "fixture-provider",
    "protocol": "responses",
    "api_mode": "http",
    "continuation_mode": "standalone",
    "supports_function_call_output": True,
    "requires_call_id": True,
}


def check(label: str, ok: bool, failures: list[str]) -> None:
    print(f"{'PASS' if ok else 'FAIL'} | {label}")
    if not ok:
        failures.append(label)


def fixture(root: Path) -> tuple[Path, Path]:
    repo = root / "developer-repo"
    (repo / "skill/references").mkdir(parents=True)
    (repo / "templates").mkdir()
    (repo / "scripts").mkdir()
    (repo / "problem/raw").mkdir(parents=True)
    (repo / "skill/SKILL.md").write_text("runtime skill", encoding="utf-8")
    for name in RUNTIME_TEMPLATE_FILES:
        (repo / "templates" / name).write_text(name, encoding="utf-8")
    for name in RUNTIME_SCRIPT_FILES:
        (repo / "scripts" / name).write_text(name, encoding="utf-8")
    for relative in RUNTIME_SUPPORT_FILES:
        (repo / relative).parent.mkdir(parents=True, exist_ok=True)
        (repo / relative).write_text("runtime compliance reference", encoding="utf-8")
    artifacts = []
    for index, name in enumerate(("problem.docx", "attachment1.xlsx", "attachment2.xlsx", "attachment3.xlsx", "attachment4.xlsx"), 1):
        data = f"fixture-{index}".encode()
        (repo / "problem/raw" / name).write_bytes(data)
        artifacts.append({"id": f"ART-{index:03d}", "filename": name, "raw_path": f"raw/{name}", "sha256": hashlib.sha256(data).hexdigest()})
    source = repo / "problem/source.yaml"
    source.write_text(yaml.safe_dump({"artifacts": artifacts}, sort_keys=False), encoding="utf-8")
    prepared = prepare_clean_room(repo, "tiny", "run-v27", source, output_root=root / "prepared").root
    return prepared, repo


def main() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="huawei-cup-v27-") as temp:
        root = Path(temp)
        prepared, repo = fixture(root)

        direct = verify_runtime_binding(prepared, prepared, run_id="run-v27", attempt_id="attempt-direct", developer_repository=repo)
        check("direct binding passes", direct["binding_mode"] == "DIRECT" and direct["binding_status"] == "PASS", failures)

        mirror = root / "managed-mirror"
        shutil.copytree(prepared, mirror)
        managed = verify_runtime_binding(prepared, mirror, run_id="run-v27", attempt_id="attempt-mirror", developer_repository=repo)
        check("managed mirror passes with equivalent hashes", managed["binding_mode"] == "MANAGED_MIRROR" and managed["binding_status"] == "PASS", failures)
        check("managed mirror checks every visible file", bool(managed["required_runtime_paths"]) and all(item["status"] == "PASS" for item in managed["required_runtime_paths"]), failures)
        check("managed mirror writable workspace passes", managed["writable_root_status"] == "PASS", failures)

        empty = root / "empty"
        (empty / "outputs").mkdir(parents=True)
        (empty / "work").mkdir()
        empty_report = verify_runtime_binding(prepared, empty, run_id="run-v27", attempt_id="attempt-empty", developer_repository=repo)
        check("empty managed root fails", empty_report["binding_status"] == "FAIL" and empty_report["missing_runtime_paths"], failures)

        no_skill = root / "no-skill"
        shutil.copytree(prepared, no_skill)
        (no_skill / "skill/SKILL.md").unlink()
        check("missing Skill fails", verify_runtime_binding(prepared, no_skill, run_id="run-v27", attempt_id="attempt-skill", developer_repository=repo)["binding_status"] == "FAIL", failures)

        no_input = root / "no-input"
        shutil.copytree(prepared, no_input)
        (no_input / "input/attachment1.xlsx").unlink()
        check("missing input fails", verify_runtime_binding(prepared, no_input, run_id="run-v27", attempt_id="attempt-input", developer_repository=repo)["binding_status"] == "FAIL", failures)

        forbidden = root / "forbidden"
        shutil.copytree(prepared, forbidden)
        (forbidden / "evaluation.yaml").write_text("score: 0", encoding="utf-8")
        forbidden_report = verify_runtime_binding(prepared, forbidden, run_id="run-v27", attempt_id="attempt-forbidden", developer_repository=repo)
        check("evaluator artifact fails actual-root scan", forbidden_report["binding_status"] == "FAIL" and forbidden_report["forbidden_matches"], failures)

        mismatch = root / "mismatch"
        shutil.copytree(prepared, mismatch)
        (mismatch / "skill/SKILL.md").write_text("tampered", encoding="utf-8")
        mismatch_report = verify_runtime_binding(prepared, mismatch, run_id="run-v27", attempt_id="attempt-mismatch", developer_repository=repo)
        check("runtime hash mismatch fails", mismatch_report["binding_status"] == "FAIL" and "skill/SKILL.md" in mismatch_report["hash_mismatches"], failures)

        repo_root = repo / "inside-developer-repo"
        shutil.copytree(prepared, repo_root)
        repo_report = verify_runtime_binding(prepared, repo_root, run_id="run-v27", attempt_id="attempt-repo", developer_repository=repo)
        check("developer repository root is rejected", repo_report["binding_status"] == "FAIL" and repo_report["developer_repository_visible"] is True, failures)

        check("valid function call pair passes", validate_function_call_pairs([{"type": "function_call", "call_id": "call_1"}, {"type": "function_call_output", "call_id": "call_1"}])["status"] == "PASS", failures)
        check("orphan function output fails", validate_function_call_pairs([{"type": "function_call_output", "call_id": "call_1"}])["status"] == "TRANSPORT_PROTOCOL_FAIL", failures)
        check("missing call_id fails", validate_function_call_pairs([{"type": "function_call_output"}])["status"] == "TRANSPORT_PROTOCOL_FAIL", failures)
        check("wrong call_id fails", validate_function_call_pairs([{"type": "function_call", "call_id": "call_1"}, {"type": "function_call_output", "call_id": "call_2"}])["status"] == "TRANSPORT_PROTOCOL_FAIL", failures)
        check("unknown provider capability is not guessed", transport_preflight(None)["preflight_status"] == "UNKNOWN", failures)
        check("known transport capability preflight passes", transport_preflight(CAPABILITIES, [{"type": "function_call", "call_id": "call_1"}, {"type": "function_call_output", "call_id": "call_1"}])["preflight_status"] == "PASS", failures)

        gated = preflight_launch(prepared, empty, run_id="run-v27", attempt_id="attempt-gated", transport_capabilities=CAPABILITIES, transport_events=[{"type": "function_call_output", "call_id": "orphan"}], developer_repository=repo)
        check("failed preflight blocks Turn 1", gated["turn1_allowed"] is False and gated["model_invocation_count"] == 0 and gated["startup_state"][-1] == "ABORT_BEFORE_TURN_1", failures)

    print(f"\nRuntime Binding Regression: {'PASS' if not failures else 'FAIL'} ({17 - len(failures)}/17 checks)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
