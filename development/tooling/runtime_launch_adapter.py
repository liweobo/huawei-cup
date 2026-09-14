"""Verify the runtime a platform actually exposes before a benchmark turn.

``prepare_clean_room.py`` defines the intended model-visible bundle.  This
module is the host-side adapter that verifies a direct or platform-managed
mirror of that bundle, checks the sole writable directory, and validates the
Responses function-call contract before allowing Turn 1.  It deliberately
does not invoke a model or mutate benchmark transcripts.
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

import yaml

sys.dont_write_bytecode = True

try:  # Support both ``import scripts...`` and direct CLI execution.
    from .prepare_clean_room import (
        CleanRoomError,
        prepare_clean_room,
        scan_visibility,
        sha256,
        validate_generated_path,
    )
except ImportError:  # pragma: no cover - exercised by the CLI entry point.
    from prepare_clean_room import (  # type: ignore
        CleanRoomError,
        prepare_clean_room,
        scan_visibility,
        sha256,
        validate_generated_path,
    )


UNKNOWN = "UNKNOWN"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _known(value: Any) -> bool:
    return value not in (None, "", UNKNOWN)


def _file_type(path: Path) -> str:
    if path.is_symlink():
        return "symlink"
    if path.is_file():
        return "file"
    if path.is_dir():
        return "directory"
    return "missing"


def _visible_files(root: Path) -> list[str]:
    return sorted(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and not path.is_symlink()
    )


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise CleanRoomError(f"cannot read runtime metadata: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CleanRoomError(f"runtime metadata must be a mapping: {path}")
    return value


def _same_path(left: Path, right: Path) -> bool:
    try:
        return left.resolve() == right.resolve()
    except OSError:
        return False


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False


def _required_paths(prepared_root: Path, manifest: Mapping[str, Any]) -> list[str]:
    if not manifest.get("runtime_allowlist"):
        raise CleanRoomError("clean-room manifest has no runtime allowlist")
    # Recompute from the prepared tree.  The persisted visibility report was
    # written before it existed, so its own file is intentionally absent from
    # that historical list.
    return _visible_files(prepared_root)


def _empty_binding_report(
    *,
    run_id: str,
    attempt_id: str,
    prepared_root: Path,
    actual_root: Path | None,
    manifest_hash: str,
    binding_mode: str = "UNBOUND",
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "run_id": run_id,
        "attempt_id": attempt_id,
        "prepared_clean_room_root": str(prepared_root),
        "actual_model_root": str(actual_root) if actual_root else None,
        "binding_mode": binding_mode,
        "prepared_manifest_sha256": manifest_hash,
        "required_runtime_paths": [],
        "missing_runtime_paths": [],
        "hash_mismatches": [],
        "unexpected_paths": [],
        "forbidden_matches": [],
        "developer_repository_visible": UNKNOWN,
        "prior_runs_visible": UNKNOWN,
        "evaluator_files_visible": UNKNOWN,
        "writable_root": "workspace",
        "writable_root_status": "UNKNOWN",
        "filesystem_isolation_level": "UNKNOWN",
        "binding_status": "UNKNOWN",
    }


def verify_runtime_binding(
    prepared_clean_room_root: str | Path,
    actual_model_root: str | Path | None,
    *,
    run_id: str,
    attempt_id: str,
    developer_repository: str | Path | None = None,
    platform_sandbox_verified: bool = False,
) -> dict[str, Any]:
    """Compare the actual model root with a prepared clean-room bundle.

    A different absolute path is valid when every model-visible file has the
    same relative path, regular-file type, and SHA256.  Missing roots, empty
    managed mirrors, symlinks, forbidden artifacts, extra files, and writes
    outside ``workspace/`` fail closed.
    """
    prepared = Path(prepared_clean_room_root).resolve()
    manifest_path = prepared / "clean-room-manifest.yaml"
    portable = (prepared / "runtime-manifest.yaml").is_file()
    if portable:
        manifest_path = prepared / "runtime-manifest.yaml"
    if not prepared.is_dir() or not manifest_path.is_file():
        raise CleanRoomError("prepared clean room or clean-room-manifest.yaml is missing")
    manifest = _load_yaml(manifest_path)
    manifest_hash = sha256(manifest_path)
    report = _empty_binding_report(
        run_id=run_id,
        attempt_id=attempt_id,
        prepared_root=prepared,
        actual_root=Path(actual_model_root).resolve() if actual_model_root else None,
        manifest_hash=manifest_hash,
    )
    if manifest.get("run_id") != run_id:
        report["binding_status"] = "FAIL"
        report["binding_failure"] = "prepared manifest run_id mismatch"
        return report
    if portable:
        try:
            from .validate_runtime_bundle import validate_runtime_bundle
        except ImportError:
            from validate_runtime_bundle import validate_runtime_bundle
        errors = validate_runtime_bundle(prepared, expected_run_id=run_id)
        if errors:
            report["binding_status"] = "FAIL"
            report["binding_failure"] = "; ".join(errors)
            return report

    prepared_scan = scan_visibility(prepared, run_id)
    if prepared_scan.get("status") != "PASS":
        report["forbidden_matches"] = list(prepared_scan.get("forbidden_matches", []))
        report["binding_status"] = "FAIL"
        return report

    actual = Path(actual_model_root).resolve() if actual_model_root else None
    if actual is None or not actual.is_dir():
        report["binding_status"] = "FAIL"
        report["binding_failure"] = "actual model-visible root is missing or not a directory"
        return report
    if developer_repository and _is_within(actual, Path(developer_repository)):
        report["developer_repository_visible"] = True
        report["binding_status"] = "FAIL"
        report["binding_failure"] = "actual model root is inside developer repository"
        return report
    if portable:
        errors = validate_runtime_bundle(actual, expected_run_id=run_id, expected_manifest_sha256=manifest_hash)
        if errors:
            report["portable_validation_errors"] = errors

    required = _required_paths(prepared, manifest)
    expected: dict[str, dict[str, str]] = {}
    for relative in required:
        source = prepared / relative
        expected[relative] = {"sha256": sha256(source), "file_type": _file_type(source)}

    actual_scan = scan_visibility(actual, run_id)
    report["forbidden_matches"] = list(actual_scan.get("forbidden_matches", []))
    report["required_runtime_paths"] = []
    for relative in required:
        candidate = actual / relative
        actual_type = _file_type(candidate)
        expected_record = expected[relative]
        actual_hash = sha256(candidate) if actual_type == "file" else None
        status = "PASS" if actual_type == "file" and actual_hash == expected_record["sha256"] else "FAIL"
        report["required_runtime_paths"].append(
            {
                "path": relative,
                "expected_sha256": expected_record["sha256"],
                "actual_sha256": actual_hash,
                "expected_file_type": expected_record["file_type"],
                "actual_file_type": actual_type,
                "status": status,
            }
        )
        if status != "PASS":
            if actual_type == "missing":
                report["missing_runtime_paths"].append(relative)
            else:
                report["hash_mismatches"].append(relative)

    actual_paths = set(_visible_files(actual))
    expected_paths = set(required)
    report["unexpected_paths"] = sorted(actual_paths - expected_paths)

    report["developer_repository_visible"] = False
    scanned_paths = list(actual_scan.get("visible_paths", [])) + list(actual_scan.get("forbidden_matches", []))
    report["evaluator_files_visible"] = bool(report["forbidden_matches"])
    report["prior_runs_visible"] = any(
        "run-001" in value or "run-002" in value or "run-003" in value
        for value in scanned_paths
    )
    writable_ok, writable_error = verify_writable_root(actual, run_id)
    report["writable_root_status"] = "PASS" if writable_ok else "FAIL"
    if writable_error:
        report["writable_root_error"] = writable_error

    clean = (
        actual_scan.get("status") == "PASS"
        and not report["missing_runtime_paths"]
        and not report["hash_mismatches"]
        and not report["unexpected_paths"]
        and report["writable_root_status"] == "PASS"
        and not report.get("portable_validation_errors")
    )
    if clean:
        report["binding_mode"] = "DIRECT" if _same_path(prepared, actual) else "MANAGED_MIRROR"
        report["binding_status"] = "PASS"
        report["filesystem_isolation_level"] = (
            "PLATFORM_SANDBOX_VERIFIED" if platform_sandbox_verified else "PROJECT_ROOT_VERIFIED"
        )
    else:
        report["binding_mode"] = "UNBOUND"
        report["binding_status"] = "FAIL"
    return report


def verify_writable_root(actual_model_root: str | Path, run_id: str) -> tuple[bool, str | None]:
    """Host-side write probe for the only permitted runtime write root."""
    root = Path(actual_model_root).resolve()
    workspace = root / "workspace"
    if not workspace.is_dir():
        return False, "actual model root has no workspace directory"
    if workspace.resolve().parent != root or workspace.is_symlink():
        return False, "workspace resolves outside the actual model root"
    probe = workspace / f".preflight-write-test-{uuid.uuid4().hex}"
    if not validate_generated_path(probe, workspace):
        return False, "workspace probe is outside writable root"
    created = False
    try:
        with probe.open("x", encoding="utf-8") as handle:
            created = True
            handle.write("preflight")
        if not probe.is_file():
            return False, "workspace probe was not created"
    except OSError as exc:
        return False, f"workspace write failed: {exc}"
    finally:
        try:
            if created:
                probe.unlink(missing_ok=True)
        except OSError:
            pass
    return True, None


def validate_function_call_pairs(events: Iterable[Mapping[str, Any]] | None) -> dict[str, Any]:
    """Validate function-call/output pairing without contacting a provider."""
    errors: list[str] = []
    calls: set[str] = set()
    outputs: set[str] = set()
    call_count = 0
    output_count = 0
    for index, event in enumerate(events or [], start=1):
        item = event.get("item") if isinstance(event, Mapping) and isinstance(event.get("item"), Mapping) else event
        if not isinstance(item, Mapping):
            continue
        event_type = str(item.get("type", "")).lower()
        if event_type == "function_call":
            call_count += 1
            value = item.get("call_id")
            call_id = value.strip() if isinstance(value, str) else ""
            if not call_id:
                errors.append(f"event {index}: function_call is missing call_id")
            elif call_id in calls:
                errors.append(f"event {index}: duplicate function_call call_id {call_id}")
            else:
                calls.add(call_id)
        elif event_type == "function_call_output":
            output_count += 1
            value = item.get("call_id")
            call_id = value.strip() if isinstance(value, str) else ""
            if not call_id:
                errors.append(f"event {index}: function_call_output is missing call_id")
            elif call_id not in calls:
                errors.append(f"event {index}: orphan function_call_output call_id {call_id}")
            elif call_id in outputs:
                errors.append(f"event {index}: duplicate function_call_output call_id {call_id}")
            else:
                outputs.add(call_id)
    return {
        "status": "PASS" if not errors else "TRANSPORT_PROTOCOL_FAIL",
        "errors": errors,
        "function_calls": call_count,
        "function_call_outputs": output_count,
        "paired_call_ids": sorted(calls & outputs),
    }


def transport_preflight(
    capabilities: Mapping[str, Any] | None,
    events: Iterable[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a capability report; unknown provider fields remain UNKNOWN."""
    caps = _as_mapping(capabilities)
    pair_report = validate_function_call_pairs(events)
    result = {
        "provider": caps.get("provider", UNKNOWN),
        "protocol": caps.get("protocol", UNKNOWN),
        "api_mode": caps.get("api_mode", UNKNOWN),
        "continuation_mode": caps.get("continuation_mode", UNKNOWN),
        "supports_function_call_output": caps.get("supports_function_call_output", UNKNOWN),
        "requires_call_id": caps.get("requires_call_id", UNKNOWN),
        "previous_response_mode": caps.get("previous_response_mode", UNKNOWN),
        "websocket_version": caps.get("websocket_version", UNKNOWN),
        "pairing": pair_report,
    }
    if result["supports_function_call_output"] is False and (pair_report["function_call_outputs"] or pair_report["function_calls"]):
        pair_report["errors"].append("provider capability reports function_call_output is unsupported")
        pair_report["status"] = "TRANSPORT_PROTOCOL_FAIL"
    capability_known = all(
        _known(result[field])
        for field in ("provider", "protocol", "api_mode", "continuation_mode", "supports_function_call_output", "requires_call_id")
    )
    if pair_report["status"] != "PASS":
        result["preflight_status"] = "TRANSPORT_PROTOCOL_FAIL"
    elif capability_known:
        result["preflight_status"] = "PASS"
    else:
        result["preflight_status"] = "UNKNOWN"
    return result


def preflight_launch(
    prepared_clean_room_root: str | Path,
    actual_model_root: str | Path | None,
    *,
    run_id: str,
    attempt_id: str,
    transport_capabilities: Mapping[str, Any] | None = None,
    transport_events: Iterable[Mapping[str, Any]] | None = None,
    developer_repository: str | Path | None = None,
    platform_sandbox_verified: bool = False,
) -> dict[str, Any]:
    """Run all host-side gates and return whether Turn 1 may be sent."""
    prepared = Path(prepared_clean_room_root).resolve()
    binding = verify_runtime_binding(
        prepared,
        actual_model_root,
        run_id=run_id,
        attempt_id=attempt_id,
        developer_repository=developer_repository,
        platform_sandbox_verified=platform_sandbox_verified,
    )
    transport = transport_preflight(transport_capabilities, transport_events)
    states = ["CLEAN_ROOM_PREPARED", "TRANSPORT_PREFLIGHT"]
    if transport["preflight_status"] != "PASS":
        states.append("ABORT_BEFORE_TURN_1")
    else:
        states.extend(["SESSION_CREATED", "ACTUAL_ROOT_RESOLVED"])
        if binding["binding_status"] != "PASS":
            states.append("ABORT_BEFORE_TURN_1")
        else:
            states.extend(["RUNTIME_BINDING_VERIFIED", "VISIBILITY_SCAN_PASS", "WRITE_ROOT_VERIFIED", "READY_FOR_MODEL_TURN_1"])
    ready = states[-1] == "READY_FOR_MODEL_TURN_1"
    return {
        "schema_version": 1,
        "run_id": run_id,
        "attempt_id": attempt_id,
        "startup_state": states,
        "launch_status": "READY_FOR_MODEL_TURN_1" if ready else "BLOCKED_BY_PLATFORM",
        "turn1_allowed": ready,
        "binding": binding,
        "transport": transport,
        "model_invocation_count": 0,
    }


def write_yaml(path: str | Path, data: Mapping[str, Any]) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(yaml.safe_dump(dict(data), allow_unicode=True, sort_keys=False), encoding="utf-8")
    return target


def write_runtime_binding_report(path: str | Path, report: Mapping[str, Any]) -> Path:
    """Persist the host-side actual-root binding report."""
    return write_yaml(path, report)


class RuntimeLaunchAdapter:
    """Small orchestration facade; platform session creation stays external."""

    def __init__(self, developer_repository: str | Path):
        self.developer_repository = Path(developer_repository).resolve()

    def prepare(self, benchmark_id: str, run_id: str, problem_source: str | Path | Mapping[str, Any]) -> Any:
        return prepare_clean_room(self.developer_repository, benchmark_id, run_id, problem_source)

    def preflight(
        self,
        prepared_clean_room_root: str | Path,
        actual_model_root: str | Path | None,
        *,
        run_id: str,
        attempt_id: str,
        transport_capabilities: Mapping[str, Any] | None = None,
        transport_events: Iterable[Mapping[str, Any]] | None = None,
        platform_sandbox_verified: bool = False,
    ) -> dict[str, Any]:
        return preflight_launch(
            prepared_clean_room_root,
            actual_model_root,
            run_id=run_id,
            attempt_id=attempt_id,
            transport_capabilities=transport_capabilities,
            transport_events=transport_events,
            developer_repository=self.developer_repository,
            platform_sandbox_verified=platform_sandbox_verified,
        )

    def launch(
        self,
        benchmark_id: str,
        run_id: str,
        problem_source: str | Path | Mapping[str, Any],
        *,
        attempt_id: str,
        session_factory: Callable[[Path], str | Path | None] | None = None,
        transport_capabilities: Mapping[str, Any] | None = None,
        transport_events: Iterable[Mapping[str, Any]] | None = None,
        platform_sandbox_verified: bool = False,
    ) -> dict[str, Any]:
        """Prepare a room and ask an injected platform launcher for its root."""
        prepared = self.prepare(benchmark_id, run_id, problem_source)
        if session_factory is None:
            return {
                "schema_version": 1,
                "run_id": run_id,
                "attempt_id": attempt_id,
                "launch_status": "BLOCKED_BY_PLATFORM",
                "turn1_allowed": False,
                "model_invocation_count": 0,
                "startup_state": ["CLEAN_ROOM_PREPARED", "SESSION_CREATE_UNAVAILABLE", "ABORT_BEFORE_TURN_1"],
                "prepared_clean_room_root": str(prepared.root),
                "failure_owner": "PLATFORM",
                "failure_category": "WORKSPACE_BINDING",
            }
        try:
            actual_root = session_factory(prepared.root)
        except Exception as exc:  # platform errors are recorded, never retried here
            return {
                "schema_version": 1,
                "run_id": run_id,
                "attempt_id": attempt_id,
                "launch_status": "BLOCKED_BY_PLATFORM",
                "turn1_allowed": False,
                "model_invocation_count": 0,
                "startup_state": ["CLEAN_ROOM_PREPARED", "SESSION_CREATE_FAILED", "ABORT_BEFORE_TURN_1"],
                "prepared_clean_room_root": str(prepared.root),
                "failure_owner": "PLATFORM",
                "failure_category": "WORKSPACE_BINDING",
                "platform_error": str(exc),
            }
        return self.preflight(
            prepared.root,
            actual_root,
            run_id=run_id,
            attempt_id=attempt_id,
            transport_capabilities=transport_capabilities,
            transport_events=transport_events,
            platform_sandbox_verified=platform_sandbox_verified,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepared-root", type=Path, required=True)
    parser.add_argument("--actual-root", type=Path)
    parser.add_argument("--developer-repository", type=Path)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--transport-capability", type=Path)
    parser.add_argument("--transport-events", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--binding-report", type=Path)
    args = parser.parse_args()
    capabilities: Mapping[str, Any] | None = None
    events: list[Mapping[str, Any]] | None = None
    if args.transport_capability:
        capabilities = _load_yaml(args.transport_capability)
    if args.transport_events:
        loaded = json.loads(args.transport_events.read_text(encoding="utf-8"))
        if not isinstance(loaded, list):
            raise SystemExit("transport events must be a JSON list")
        events = [item for item in loaded if isinstance(item, Mapping)]
    result = preflight_launch(
        args.prepared_root,
        args.actual_root,
        run_id=args.run_id,
        attempt_id=args.attempt_id,
        transport_capabilities=capabilities,
        transport_events=events,
        developer_repository=args.developer_repository,
    )
    if args.report:
        write_yaml(args.report, result)
    if args.binding_report:
        write_runtime_binding_report(args.binding_report, result["binding"])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["turn1_allowed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
