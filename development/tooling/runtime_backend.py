"""Minimal external execution-backend contract for portable runtimes."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Mapping, Protocol


BACKEND_KINDS = ("LOCAL_CONTROLLED", "CONTAINER", "MANAGED_WORKSPACE")
FILESYSTEM_ISOLATION_LEVELS = (
    "PROJECT_ROOT_ONLY",
    "CONTAINER_ISOLATED",
    "PLATFORM_SANDBOX",
    "UNKNOWN",
)


class RuntimeBackend(Protocol):
    """The small host-side interface an external runner must implement."""

    kind: str

    def prepare(self, bundle_root: Path) -> None:
        """Make the bundle the only model-visible project or mount."""

    def resolve_model_root(self) -> Path | None:
        """Return the actual model-visible root, or ``None`` if unavailable."""

    def inspect_visible_files(self) -> Mapping[str, Any]:
        """Return host/runtime metadata for the actual visible tree."""

    def inspect_write_root(self) -> Mapping[str, Any]:
        """Verify that only ``workspace/`` is writable."""

    def transport_preflight(self) -> Mapping[str, Any]:
        """Probe provider transport before a benchmark turn is submitted."""


def backend_contract(kind: str) -> dict[str, Any]:
    """Return declarative requirements for a supported backend kind."""
    normalized = str(kind).upper()
    if normalized not in BACKEND_KINDS:
        raise ValueError(f"unsupported runtime backend: {kind}")
    isolation = {
        "LOCAL_CONTROLLED": "PROJECT_ROOT_ONLY",
        "CONTAINER": "CONTAINER_ISOLATED",
        "MANAGED_WORKSPACE": "PLATFORM_SANDBOX",
    }[normalized]
    return {
        "backend": normalized,
        "bundle_root_is_model_root": True,
        "writable_root": "workspace/",
        "developer_repository_mounted": False,
        "prior_runs_mounted": False,
        "required_isolation_level": isolation,
        "filesystem_isolation_level": "UNKNOWN",
        "capability_evidence_required": True,
        "transport_preflight_required": True,
        "fresh_conversation_required": True,
    }


def export_workspace_outputs(
    bundle_root: str | Path, output: str | Path, *,
    snapshot: Mapping[str, Any], session_stopped: bool,
    execution_metadata: Mapping[str, Any],
) -> Path:
    """Transfer raw workspace files only after the external runner stops.

    The runner supplies the stop attestation and the trusted pre-run snapshot.
    This helper cannot stop or inspect a platform session itself.
    """
    try:
        from .validate_runtime_bundle import validate_immutable_snapshot, validate_runtime_bundle, sha256
    except ImportError:
        from validate_runtime_bundle import validate_immutable_snapshot, validate_runtime_bundle, sha256
    if session_stopped is not True:
        raise ValueError("stop the model session before exporting outputs")
    root = Path(bundle_root).resolve()
    destination = Path(output).resolve()
    if destination.exists() or destination.is_relative_to(root) or root.is_relative_to(destination):
        raise ValueError("output must be a new directory outside the runtime bundle")
    errors = validate_immutable_snapshot(root, snapshot) + validate_runtime_bundle(root, post_run=True)
    if errors:
        raise ValueError("RUNTIME_INTEGRITY_FAIL: " + "; ".join(errors))
    # Serialize host metadata before creating a destination to avoid partial
    # transfers for unsupported values.
    metadata = json.loads(json.dumps(dict(execution_metadata)))
    created = False
    try:
        destination.mkdir(parents=True)
        created = True
        shutil.copytree(root / "workspace", destination / "workspace")
        records = []
        for file in sorted((root / "workspace").rglob("*")):
            if not file.is_file():
                continue
            relative = file.relative_to(root).as_posix()
            digest = sha256(file)
            if sha256(destination / relative) != digest:
                raise ValueError(f"output transfer hash mismatch: {relative}")
            records.append({"relative_path": relative, "sha256": digest})
        report = {
            "schema_version": 1, "session_stopped": True,
            "runtime_manifest_sha256": snapshot["manifest_sha256"],
            "runtime_integrity_status": "RUNTIME_INTEGRITY_PASS",
            "files": records, "execution_metadata": metadata,
        }
        (destination / "runtime-execution-metadata.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        return destination
    except Exception:
        if created:
            shutil.rmtree(destination)
        raise
