"""Export a clean-room runtime as a self-contained portable bundle."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml

try:
    from .prepare_clean_room import CleanRoomError, hash_directory, prepare_clean_room, sha256
    from .validate_runtime_bundle import _hash_records, validate_runtime_bundle
    from .runtime_launch_adapter import transport_preflight
except ImportError:  # pragma: no cover - direct CLI execution
    from prepare_clean_room import CleanRoomError, hash_directory, prepare_clean_room, sha256  # type: ignore
    from validate_runtime_bundle import _hash_records, validate_runtime_bundle  # type: ignore
    from runtime_launch_adapter import transport_preflight  # type: ignore


EXPORTER_VERSION = "V2.8 Phase 2"
PORTABLE_RUNNER_FILES = (
    "prepare_clean_room.py",
    "runtime_backend.py",
    "runtime_launch_adapter.py",
    "validate_runtime_bundle.py",
)


@dataclass(frozen=True)
class RuntimeBundleResult:
    bundle_root: Path
    manifest_path: Path
    zip_path: Path | None
    zip_sha256_path: Path | None
    receipt_path: Path


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CleanRoomError(f"source record must be a mapping: {path}")
    return value


def _find_problem_source(developer_repo: Path, benchmark_id: str, problem_source: str | Path | None) -> Path:
    if problem_source is not None:
        source = Path(problem_source)
        if not source.is_absolute():
            source = developer_repo / source
        if not source.is_file():
            raise CleanRoomError(f"problem source does not exist: {source}")
        return source.resolve()
    candidates = sorted((developer_repo / "development/benchmarks/problems").rglob("source.yaml"))
    for candidate in candidates:
        try:
            record = _load_yaml(candidate)
        except (OSError, UnicodeError, yaml.YAMLError, CleanRoomError):
            continue
        if str(record.get("benchmark_id", "")) == benchmark_id:
            return candidate.resolve()
    raise CleanRoomError(f"no source.yaml found for benchmark_id={benchmark_id}")


def _frozen_user_script_hash(source_path: Path) -> str:
    candidate = source_path.parent / "user-turns.yaml"
    if not candidate.is_file():
        raise CleanRoomError("frozen user-turns.yaml is required for export provenance")
    return sha256(candidate)


def _role(relative: str) -> str:
    first = Path(relative).parts[:1]
    if first == ("skill",):
        return "skill_runtime"
    if first == ("scripts",):
        return "runtime_script"
    if first == ("templates",):
        return "runtime_template"
    if first == ("input",):
        return "problem_input"
    if first == ("compliance",):
        return "runtime_support"
    if relative == "runtime-requirements.yaml":
        return "runtime_contract"
    if relative == "launch-preflight.json":
        return "launch_metadata"
    return "runtime_metadata"


def _write_yaml(path: Path, value: Mapping[str, Any]) -> None:
    path.write_text(yaml.safe_dump(dict(value), allow_unicode=True, sort_keys=False), encoding="utf-8")


def _write_launch_preflight(path: Path, run_id: str) -> None:
    payload = {
        "schema_version": 1,
        "run_id": run_id,
        "bundle_root": ".",
        "launch_status": "PLATFORM_SELECTION_REQUIRED",
        "turn1_allowed": False,
        "model_invocation_count": 0,
        "binding": {
            "binding_mode": "PENDING_EXTERNAL_BACKEND",
            "binding_status": "UNKNOWN",
            "filesystem_isolation_level": "UNKNOWN",
            "actual_model_root": "UNKNOWN",
        },
        "transport": transport_preflight(None),
        "note": "External backend must rerun V2.7 actual-root and transport preflight before Turn 1.",
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _zip_bundle(bundle_root: Path, zip_path: Path) -> Path:
    if zip_path.exists():
        raise FileExistsError(f"bundle zip already exists: {zip_path}")
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    root_name = bundle_root.name
    with zipfile.ZipFile(zip_path, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(bundle_root.rglob("*")):
            if path.is_symlink():
                raise CleanRoomError("cannot zip linked runtime files")
            relative = f"{root_name}/{path.relative_to(bundle_root).as_posix()}"
            if path.is_dir():
                archive.writestr(relative + "/", b"")
            elif path.is_file():
                archive.write(path, relative)
    return zip_path


def export_runtime_bundle(
    developer_repo: str | Path,
    benchmark_id: str,
    run_id: str,
    output: str | Path,
    *,
    problem_source: str | Path | None = None,
    make_zip: bool = False,
) -> RuntimeBundleResult:
    """Prepare once, export allowlisted content, and validate independently."""
    repo = Path(developer_repo).resolve()
    output_root = Path(output).resolve()
    if output_root.exists():
        raise FileExistsError(f"bundle output already exists: {output_root}")
    if output_root.is_relative_to(repo) and not output_root.is_relative_to(repo / "dist"):
        raise CleanRoomError("repository-local exports must stay under dist/")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", run_id):
        raise CleanRoomError("invalid run_id")
    source = _find_problem_source(repo, benchmark_id, problem_source)
    source_benchmark = _load_yaml(source).get("benchmark_id")
    if source_benchmark and source_benchmark != benchmark_id:
        raise CleanRoomError("problem source benchmark_id mismatch")
    frozen_hash = _frozen_user_script_hash(source)
    receipt_path = output_root.with_name(output_root.name + ".export-receipt.yaml")
    zip_path = output_root.with_name(output_root.name + ".zip") if make_zip else None
    zip_sha_path = Path(str(zip_path) + ".sha256") if zip_path else None
    for path in (receipt_path, zip_path, zip_sha_path):
        if path and path.exists():
            raise FileExistsError(f"export artifact already exists: {path}")
    staging_parent = Path(tempfile.mkdtemp(prefix=f"huawei-cup-{run_id}-export-"))
    staging_root = staging_parent / "clean-room"
    created_output = False
    created_files: list[Path] = []
    try:
        prepared = prepare_clean_room(repo, benchmark_id, run_id, source, output_root=staging_root)
        clean_manifest = _load_yaml(prepared.manifest_path)
        output_root.mkdir(parents=True)
        created_output = True
        # The builder's manifest is the only selection policy. Never copy a
        # developer tree, and never retain links to canonical input in exports.
        for group in clean_manifest["runtime_allowlist"].values():
            for relative in group:
                target = output_root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(prepared.root / relative, target)
        for directory in ("input", "workspace"):
            shutil.copytree(prepared.root / directory, output_root / directory)
        # Runner utilities are shipped for out-of-band validation only.  They
        # are not part of the model-readable Skill tree and are not selected
        # by the runtime read contract.
        runner_dir = output_root / "scripts"
        runner_dir.mkdir(parents=True, exist_ok=True)
        tooling_dir = Path(__file__).resolve().parent
        for name in PORTABLE_RUNNER_FILES:
            shutil.copy2(tooling_dir / name, runner_dir / name)

        _write_yaml(
            output_root / "runtime-requirements.yaml",
            {
                "schema_version": 1,
                "bundle_root": ".",
                "workspace": {"root_must_be_bundle_root": True, "writable_paths": ["workspace/"]},
                "filesystem": {"developer_repository_not_mounted": True, "prior_runs_not_mounted": True},
                "python": {
                    "required": True, "minimum": ">=3.10",
                    "packages": ["pyyaml", "numpy", "pandas", "scikit-learn", "openpyxl", "matplotlib"],
                    "environment": {"PYTHONDONTWRITEBYTECODE": "1", "MPLCONFIGDIR": "workspace/.matplotlib"},
                },
                "network": {"required": "optional/according_to_skill"},
                "model": {"fresh_conversation": True, "benchmark_turns_start_after_preflight": True},
                "execution_backends": ["LOCAL_CONTROLLED", "CONTAINER", "MANAGED_WORKSPACE"],
                "external_runner_contract": {
                    "read_paths": ["skill/", "input/"],
                    "write_path": "workspace/",
                    "evaluator_repo_mounted": False,
                },
                "mutation_policy": {
                    "immutable_paths": ["skill/", "input/", "runtime-manifest.yaml", *["runtime-requirements.yaml", "launch-preflight.json"]],
                    "enforce_read_only_when_available": True,
                    "pre_post_hash_verification_required": True,
                    "trusted_snapshot_location": "outside_model_visibility",
                },
                "post_run_export": {
                    "model_session_must_be_stopped": True,
                    "paths": ["workspace/"],
                    "host_execution_metadata": True,
                    "immutable_integrity_must_pass": True,
                    "evaluator_runs_after_session_stop": True,
                },
            },
        )
        _write_launch_preflight(output_root / "launch-preflight.json", run_id)

        input_records = [
            {
                "source_artifact_id": item["source_artifact_id"],
                "relative_path": item["clean_room_path"],
                "sha256": item["runtime_sha256"],
            }
            for item in clean_manifest.get("input_artifacts", [])
        ]
        immutable_paths = sorted(
            path.relative_to(output_root).as_posix()
            for path in output_root.rglob("*")
            if path.is_file() and not path.is_symlink() and path.relative_to(output_root).parts[:1] != ("workspace",)
        )
        files = [
            {
                "relative_path": relative,
                "sha256": sha256(output_root / relative),
                "size": (output_root / relative).stat().st_size,
                "role": _role(relative),
                "file_type": "file",
            }
            for relative in immutable_paths
        ]
        manifest = {
            "schema_version": 1,
            "exporter_version": EXPORTER_VERSION,
            "benchmark_id": benchmark_id,
            "run_id": run_id,
            "skill_version": clean_manifest["skill_version"],
            "skill_hash": hash_directory(output_root / "skill"),
            "frozen_user_script_sha256": frozen_hash,
            "runtime_allowlist": {
                **clean_manifest["runtime_allowlist"],
                "runner_tools": [f"scripts/{name}" for name in PORTABLE_RUNNER_FILES],
            },
            "files": files,
            "file_count": len(files),
            "content_sha256": _hash_records(output_root, immutable_paths),
            "input_artifacts": input_records,
            "initial_workspace_files": [
                {"relative_path": path.relative_to(output_root).as_posix(), "sha256": sha256(path),
                 "size": path.stat().st_size, "role": "workspace_bootstrap", "file_type": "file"}
                for path in sorted((output_root / "workspace").rglob("*")) if path.is_file()
            ],
            "allowed_write_root": "workspace/",
            "forbidden_roots": ["../"],
            "developer_repository_required": False,
            "external_backend_required": True,
        }
        _write_yaml(output_root / "runtime-manifest.yaml", manifest)
        errors = validate_runtime_bundle(output_root, expected_run_id=run_id)
        if errors:
            raise CleanRoomError("exported runtime bundle validation failed: " + "; ".join(errors))
        if zip_path:
            created_files.append(zip_path)
            _zip_bundle(output_root, zip_path)
            # Verify the transport artifact after unpacking, including empty
            # workspace directories that ZIP tools commonly omit.
            with tempfile.TemporaryDirectory(prefix="huawei-cup-unpack-") as unpacked:
                with zipfile.ZipFile(zip_path) as archive:
                    archive.extractall(unpacked)
                errors = validate_runtime_bundle(Path(unpacked) / output_root.name,
                                                 expected_manifest_sha256=sha256(output_root / "runtime-manifest.yaml"))
                if errors:
                    raise CleanRoomError("unpacked runtime validation failed: " + "; ".join(errors))
            digest = sha256(zip_path)
            assert zip_sha_path is not None
            created_files.append(zip_sha_path)
            zip_sha_path.write_text(f"{digest}  {zip_path.name}\n", encoding="ascii")
        created_files.append(receipt_path)
        _write_yaml(receipt_path, {
            "schema_version": 1, "exporter_version": EXPORTER_VERSION,
            "benchmark_id": benchmark_id, "run_id": run_id,
            "runtime_manifest_sha256": sha256(output_root / "runtime-manifest.yaml"),
            "bundle_content_sha256": manifest["content_sha256"],
            "bundle_zip_sha256": sha256(zip_path) if zip_path else None,
            "frozen_user_script_sha256": frozen_hash,
            "skill_hash": manifest["skill_hash"], "immutable_file_count": len(files),
            "visible_file_count": len(files) + len(manifest["initial_workspace_files"]) + 1,
            "input_artifacts": input_records,
            "status": "PORTABLE_RUNTIME_READY", "platform_status": "PLATFORM_SELECTION_REQUIRED",
            "model_invocation_count": 0,
        })
        return RuntimeBundleResult(output_root, output_root / "runtime-manifest.yaml", zip_path, zip_sha_path, receipt_path)
    except Exception:
        if created_output:
            shutil.rmtree(output_root, ignore_errors=True)
        for path in created_files:
            path.unlink(missing_ok=True)
        raise
    finally:
        shutil.rmtree(staging_parent, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--developer-repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--benchmark-id", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--problem-source", type=Path)
    parser.add_argument("--zip", action="store_true", dest="make_zip")
    args = parser.parse_args()
    result = export_runtime_bundle(
        args.developer_repo,
        args.benchmark_id,
        args.run_id,
        args.output,
        problem_source=args.problem_source,
        make_zip=args.make_zip,
    )
    print(json.dumps({
        "bundle_root": str(result.bundle_root),
        "runtime_manifest": str(result.manifest_path),
        "zip": str(result.zip_path) if result.zip_path else None,
        "zip_sha256": str(result.zip_sha256_path) if result.zip_sha256_path else None,
        "export_receipt": str(result.receipt_path),
        "status": "RUNTIME_BUNDLE_VALID",
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
