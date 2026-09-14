"""Validate a portable runtime using only its own files and PyYAML.

Keep the manifest digest and immutable snapshot outside model visibility.
The shared clean-room module supplies the policy without reading a developer
repository. Validation never invokes a model or a provider.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Iterable, Mapping

import yaml

sys.dont_write_bytecode = True

try:
    from .prepare_clean_room import (
        RUNTIME_SCRIPT_FILES, RUNTIME_SUPPORT_FILES, RUNTIME_TEMPLATE_FILES,
        hash_directory, scan_visibility, sha256,
    )
except ImportError:  # pragma: no cover - bundle-local CLI
    try:
        from prepare_clean_room import (
            RUNTIME_SCRIPT_FILES, RUNTIME_SUPPORT_FILES, RUNTIME_TEMPLATE_FILES,
            hash_directory, scan_visibility, sha256,
        )
    except ImportError:
        if __name__ == "__main__":
            print("RUNTIME_BUNDLE_INVALID")
            raise SystemExit(1)
        raise


METADATA_FILES = ("runtime-requirements.yaml", "launch-preflight.json")
WORKSPACE_DIRECTORIES = ("workspace", "workspace/code", "workspace/outputs", "workspace/experiments", "workspace/evidence", "workspace/paper")


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must contain a mapping")
    return value


def _relative(value: Any) -> str:
    if not isinstance(value, str) or not value or "\\" in value or ":" in value or "\0" in value:
        raise ValueError(f"invalid portable relative path: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or PureWindowsPath(value).drive or any(part in ("", ".", "..") for part in value.split("/")):
        raise ValueError(f"path must stay inside the bundle: {value!r}")
    return value


def _linked(path: Path) -> bool:
    return path.is_symlink() or bool(getattr(path, "is_junction", lambda: False)())


def _tree(root: Path) -> tuple[list[str], list[str]]:
    files: list[str] = []
    errors: list[str] = []
    for current, directories, names in os.walk(root, followlinks=False):
        for name in list(directories) + names:
            path = Path(current) / name
            relative = path.relative_to(root).as_posix()
            if _linked(path):
                errors.append(f"linked path is forbidden: {relative}")
                if name in directories:
                    directories.remove(name)
            elif name in names:
                if path.is_file():
                    files.append(relative)
                else:
                    errors.append(f"non-regular file: {relative}")
    return sorted(files), errors


def _hash_records(root: Path, paths: Iterable[str]) -> str:
    digest = hashlib.sha256()
    for relative in sorted(paths):
        encoded = relative.encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
        with (root / relative).open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    return digest.hexdigest()


def validate_workspace_write_path(bundle_root: str | Path, path: str | Path) -> bool:
    root = Path(bundle_root).resolve()
    workspace = root / "workspace"
    try:
        if _linked(workspace) or workspace.resolve().parent != root:
            return False
        candidate = Path(path)
        if not candidate.is_absolute():
            candidate = root / _relative(str(path).replace("\\", "/"))
        resolved = candidate.resolve()
        return resolved != workspace and resolved.is_relative_to(workspace)
    except (OSError, ValueError):
        return False


def _verify_records(root: Path, records: Any, errors: list[str]) -> list[str]:
    if not isinstance(records, list) or not records:
        raise ValueError("manifest records must be a non-empty list")
    paths: list[str] = []
    for item in records:
        if not isinstance(item, dict):
            raise ValueError("file records must be mappings")
        relative = _relative(item.get("relative_path"))
        paths.append(relative)
        target = root / relative
        if item.get("file_type") != "file" or not item.get("role"):
            errors.append(f"invalid file type or role: {relative}")
        if not target.is_file() or _linked(target):
            errors.append(f"missing regular file: {relative}")
        elif sha256(target) != item.get("sha256"):
            errors.append(f"hash mismatch: {relative}")
        elif target.stat().st_size != item.get("size"):
            errors.append(f"size mismatch: {relative}")
    if len(paths) != len(set(paths)) or len(paths) != len({item.casefold() for item in paths}):
        errors.append("duplicate or case-colliding manifest paths")
    return paths


def validate_runtime_bundle(
    bundle_root: str | Path, *, expected_run_id: str | None = None,
    expected_manifest_sha256: str | None = None, post_run: bool = False,
) -> list[str]:
    """Return errors, with an empty list meaning RUNTIME_BUNDLE_VALID."""
    root = Path(bundle_root).resolve()
    if not root.is_dir() or _linked(Path(bundle_root)):
        return ["bundle root is missing or linked"]
    visible, errors = _tree(root)
    if errors:
        return errors
    try:
        manifest_path = root / "runtime-manifest.yaml"
        manifest = _load_yaml(manifest_path)
        if expected_manifest_sha256 and sha256(manifest_path) != expected_manifest_sha256:
            errors.append("trusted runtime manifest SHA256 mismatch")
        if manifest.get("schema_version") != 1:
            errors.append("unsupported runtime manifest schema")
        for field in ("benchmark_id", "run_id", "exporter_version", "skill_version"):
            if not isinstance(manifest.get(field), str) or not manifest[field]:
                errors.append(f"missing manifest field: {field}")
        for field in ("skill_hash", "content_sha256", "frozen_user_script_sha256"):
            if not re.fullmatch(r"[0-9a-f]{64}", str(manifest.get(field, ""))):
                errors.append(f"invalid SHA256: {field}")
        if expected_run_id and manifest.get("run_id") != expected_run_id:
            errors.append("runtime manifest run_id mismatch")
        if manifest.get("developer_repository_required") is not False:
            errors.append("developer_repository_required must be false")
        if manifest.get("allowed_write_root") != "workspace/" or manifest.get("forbidden_roots") != ["../"]:
            errors.append("only workspace/ may be writable")
        for directory in ("skill", "scripts", "input", *WORKSPACE_DIRECTORIES):
            if not (root / directory).is_dir():
                errors.append(f"missing runtime directory: {directory}")
        required = {
            "skill/SKILL.md", "skill/routing.yaml", *METADATA_FILES, *RUNTIME_SUPPORT_FILES,
            "scripts/prepare_clean_room.py", "scripts/runtime_backend.py",
            "scripts/runtime_launch_adapter.py", "scripts/validate_runtime_bundle.py",
        }
        for relative in sorted(required - set(visible)):
            errors.append(f"missing required runtime file: {relative}")
        paths = _verify_records(root, manifest.get("files"), errors)
        immutable = {p for p in visible if not p.startswith("workspace/") and p != "runtime-manifest.yaml"}
        if set(paths) != immutable:
            errors.append("manifest inventory differs from immutable runtime files")
        if manifest.get("file_count") != len(paths):
            errors.append("manifest file_count mismatch")
        if not errors and manifest.get("content_sha256") != _hash_records(root, paths):
            errors.append("content_sha256 mismatch")
        if manifest.get("skill_hash") != hash_directory(root / "skill"):
            errors.append("skill_hash mismatch")
        allowlist = manifest.get("runtime_allowlist")
        if not isinstance(allowlist, dict) or not allowlist:
            raise ValueError("runtime_allowlist is missing")
        allowlisted = {_relative(p) for group in allowlist.values() for p in group}
        runtime_paths = immutable - set(METADATA_FILES) - {p for p in immutable if p.startswith("input/")}
        if allowlisted != runtime_paths:
            errors.append("clean-room allowlist differs from runtime inventory")
        inputs = manifest.get("input_artifacts")
        if not isinstance(inputs, list) or not inputs:
            raise ValueError("input_artifacts must be a non-empty list")
        input_paths: set[str] = set()
        input_ids: set[str] = set()
        for item in inputs:
            relative = _relative(item["relative_path"])
            source_id = item["source_artifact_id"]
            if not isinstance(source_id, str) or not source_id or source_id in input_ids:
                errors.append("source_artifact_id must be present and unique")
            input_ids.add(source_id)
            if not relative.startswith("input/") or relative in input_paths:
                errors.append("invalid or duplicate input path")
            input_paths.add(relative)
            if not (root / relative).is_file() or sha256(root / relative) != item["sha256"]:
                errors.append(f"input artifact hash mismatch: {relative}")
        if input_paths != {p for p in immutable if p.startswith("input/")}:
            errors.append("input inventory mismatch")
        requirements = _load_yaml(root / "runtime-requirements.yaml")
        if requirements.get("workspace") != {"root_must_be_bundle_root": True, "writable_paths": ["workspace/"]}:
            errors.append("workspace environment contract mismatch")
        filesystem = requirements.get("filesystem", {})
        if filesystem.get("developer_repository_not_mounted") is not True or filesystem.get("prior_runs_not_mounted") is not True:
            errors.append("external filesystem contract mismatch")
        launch = json.loads((root / "launch-preflight.json").read_text(encoding="utf-8"))
        if launch.get("run_id") != manifest.get("run_id") or launch.get("turn1_allowed") is not False:
            errors.append("export metadata cannot authorize Turn 1")
        if not post_run:
            seeds = _verify_records(root, manifest.get("initial_workspace_files"), errors)
            if any(not p.startswith("workspace/") for p in seeds):
                errors.append("workspace seed is outside workspace/")
            if set(seeds) != {p for p in visible if p.startswith("workspace/")}:
                errors.append("pre-run workspace contains unexpected outputs")
        active = _load_yaml(root / "workspace/evidence/active-evidence-set.yaml")
        if active.get("active_run_id") != manifest.get("run_id"):
            errors.append("active evidence run_id mismatch")
        if not post_run and active.get("active_evidence_set") != {}:
            errors.append("pre-run active evidence must be empty")
        scan = scan_visibility(root, str(manifest.get("run_id")))
        errors.extend(f"forbidden visibility: {item}" for item in scan["forbidden_matches"])
    except (OSError, UnicodeError, yaml.YAMLError, ValueError, TypeError, KeyError, AttributeError) as exc:
        errors.append(f"invalid runtime bundle: {exc}")
    return errors


def capture_immutable_snapshot(bundle_root: str | Path) -> dict[str, Any]:
    root = Path(bundle_root).resolve()
    errors = validate_runtime_bundle(root)
    if errors:
        raise ValueError("cannot snapshot invalid runtime: " + "; ".join(errors))
    files, _ = _tree(root)
    return {
        "schema_version": 1,
        "manifest_sha256": sha256(root / "runtime-manifest.yaml"),
        "files": {p: sha256(root / p) for p in files if not p.startswith("workspace/")},
    }


def validate_immutable_snapshot(bundle_root: str | Path, snapshot: Mapping[str, Any]) -> list[str]:
    root = Path(bundle_root).resolve()
    files, errors = _tree(root)
    if errors:
        return errors
    try:
        expected = snapshot["files"]
        if not isinstance(expected, dict) or not expected:
            raise ValueError("immutable snapshot files must be a non-empty mapping")
        current = {p for p in files if not p.startswith("workspace/")}
        if current != set(expected):
            errors.append("immutable runtime file inventory mutated")
        for relative, digest in expected.items():
            target = root / _relative(relative)
            if not target.is_file() or sha256(target) != digest:
                errors.append(f"immutable runtime file mutated or removed: {relative}")
        if sha256(root / "runtime-manifest.yaml") != snapshot.get("manifest_sha256"):
            errors.append("runtime-manifest.yaml mutated")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        errors.append(f"invalid immutable snapshot: {exc}")
    return errors


def runtime_integrity_status(bundle_root: str | Path, snapshot: Mapping[str, Any]) -> str:
    return "RUNTIME_INTEGRITY_FAIL" if validate_immutable_snapshot(bundle_root, snapshot) else "RUNTIME_INTEGRITY_PASS"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--run-id")
    parser.add_argument("--manifest-sha256")
    parser.add_argument("--snapshot", type=Path)
    parser.add_argument("--verify-snapshot", type=Path)
    args = parser.parse_args()
    try:
        errors = validate_runtime_bundle(args.bundle, expected_run_id=args.run_id,
                                         expected_manifest_sha256=args.manifest_sha256,
                                         post_run=bool(args.verify_snapshot))
        if args.verify_snapshot:
            snapshot = json.loads(args.verify_snapshot.read_text(encoding="utf-8"))
            errors.extend(validate_immutable_snapshot(args.bundle, snapshot))
        if args.snapshot and not errors:
            if args.snapshot.resolve().is_relative_to(args.bundle.resolve()):
                raise ValueError("trusted snapshot must be outside model visibility")
            with args.snapshot.open("x", encoding="utf-8") as handle:
                json.dump(capture_immutable_snapshot(args.bundle), handle, indent=2)
    except (OSError, ValueError, TypeError, KeyError):
        errors = ["validation failed"]
    print("RUNTIME_BUNDLE_INVALID" if errors else "RUNTIME_BUNDLE_VALID")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
