"""Build and validate a clean-room runtime for a real modelling run.

The developer repository is intentionally not used as the model's working
directory.  This module copies only runtime allowlisted files and canonical
user inputs into a temporary directory, then scans the complete visible tree
before a model may start.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import yaml


# These names are retained as public metadata for the development regressions.
# The actual runtime selection is the complete, self-contained ``skill/`` tree;
# development launchers and evaluator files never enter a model-visible room.
RUNTIME_SCRIPT_FILES = ("__init__.py", "data_audit.py", "temporal_availability.py", "metrics.py",
                        "plotting.py", "robustness.py", "runtime_provenance.py", "sensitivity.py")
RUNTIME_SUPPORT_FILES: tuple[str, ...] = ()
RUNTIME_TEMPLATE_FILES: tuple[str, ...] = ()
CONTENT_MARKERS = (
    re.compile(r"(?m)^\s*expected_route\s*:", re.IGNORECASE),
    re.compile(r"(?m)^\s*known_failure\s*:", re.IGNORECASE),
    re.compile(r"(?m)^\s*evaluator_notes\s*:", re.IGNORECASE),
    re.compile(r"(?m)^\s*model_behavior_p0\s*:", re.IGNORECASE),
    re.compile(r"(?m)^\s*first_meaningful_failure\s*:", re.IGNORECASE),
    re.compile(r"(?m)^\s*rubric_score\s*:", re.IGNORECASE),
)
TEXT_SUFFIXES = {".md", ".txt", ".yaml", ".yml", ".json", ".py", ".csv", ".toml"}
FORBIDDEN_NAME_PATTERNS = (
    re.compile(r"^AGENTS\.md$", re.IGNORECASE),
    re.compile(r"^evaluation(?:\.yaml|\.yml|\.json)$", re.IGNORECASE),
    re.compile(r"^evaluation\.md$", re.IGNORECASE),
    re.compile(r"^postmortem\.md$", re.IGNORECASE),
    re.compile(r"^ground-truth\.yaml$", re.IGNORECASE),
    re.compile(r"^ground-truth\.yml$", re.IGNORECASE),
    re.compile(r"^problem-facts\.yaml$", re.IGNORECASE),
    re.compile(r"^problem-facts\.yml$", re.IGNORECASE),
    re.compile(r"^expected\.yaml$", re.IGNORECASE),
    re.compile(r"^expected\.yml$", re.IGNORECASE),
    re.compile(r"^result\.txt$", re.IGNORECASE),
    re.compile(r"^transcript\.yaml$", re.IGNORECASE),
    re.compile(r"^transcript\.yml$", re.IGNORECASE),
    re.compile(r"^model-behavior-rubric\.md$", re.IGNORECASE),
    re.compile(r"^reviewer(?:-benchmark|-notes)?(?:[-_]notes)?\.md$", re.IGNORECASE),
)
ALWAYS_FORBIDDEN_FILENAMES = {
    "agents.md",
    "evaluation.yaml", "evaluation.yml", "evaluation.json",
    "postmortem.md",
    "ground-truth.yaml", "ground-truth.yml",
    "problem-facts.yaml", "problem-facts.yml",
    "expected.yaml", "expected.yml",
    "result.txt",
    "transcript.yaml", "transcript.yml",
    "model-behavior-rubric.md",
}
FORBIDDEN_PARTS = {"benchmarks", "runs", "harness", "tests", "regression"}


class CleanRoomError(RuntimeError):
    """Raised when a clean-room invariant cannot be established."""


@dataclass(frozen=True)
class CleanRoomResult:
    root: Path
    manifest_path: Path
    visibility_report_path: Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _hash_files(root: Path, files: Iterable[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(files, key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(path.read_bytes())
    return digest.hexdigest()


def hash_directory(root: Path) -> str:
    """Hash relative paths and bytes for a deterministic runtime identity."""
    files = [path for path in root.rglob("*") if path.is_file() and not path.is_symlink()]
    return _hash_files(root, files)


def _runtime_skill_files(root: Path) -> list[Path]:
    return [
        path
        for path in root.rglob("*")
        if path.is_file() and not path.is_symlink() and "__pycache__" not in path.parts
    ]


def _copy_file(source: Path, destination: Path, *, use_hardlinks: bool) -> str:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() or destination.is_symlink():
        raise CleanRoomError(f"destination already exists: {destination}")
    if use_hardlinks:
        try:
            os.link(source, destination)
            return "hardlink"
        except (OSError, NotImplementedError):
            pass
    shutil.copy2(source, destination)
    return "copy"


def _load_source_record(problem_source: str | Path | Mapping[str, Any] | Sequence[Any], developer_repo: Path) -> tuple[list[dict[str, Any]], Path | None]:
    source_path: Path | None = None
    if isinstance(problem_source, (str, Path)):
        source_path = Path(problem_source)
        if not source_path.is_absolute():
            source_path = (developer_repo / source_path).resolve()
        if source_path.is_dir():
            source_path = source_path / "source.yaml"
        if not source_path.is_file():
            raise CleanRoomError(f"problem source record does not exist: {source_path}")
        try:
            data = yaml.safe_load(source_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            raise CleanRoomError(f"cannot read problem source record: {source_path}: {exc}") from exc
    elif isinstance(problem_source, Mapping):
        data = problem_source
    elif isinstance(problem_source, Sequence) and not isinstance(problem_source, (str, bytes, bytearray)):
        data = {"artifacts": list(problem_source)}
    else:
        raise TypeError("problem_source must be a source.yaml path, mapping, or artifact sequence")
    artifacts = data.get("artifacts") if isinstance(data, Mapping) else None
    if not isinstance(artifacts, list) or not artifacts:
        raise CleanRoomError("problem source must contain a non-empty artifacts list")
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(artifacts, start=1):
        if isinstance(item, (str, Path)):
            item = {"raw_path": str(item)}
        if not isinstance(item, Mapping):
            raise CleanRoomError(f"source artifact {index} must be a mapping or path")
        record = dict(item)
        raw_path = str(record.get("raw_path") or record.get("path") or "").strip()
        if not raw_path:
            raise CleanRoomError(f"source artifact {index} has no raw_path")
        if source_path is not None:
            raw = (source_path.parent / raw_path).resolve()
        else:
            raw = Path(raw_path)
            if not raw.is_absolute():
                raw = (developer_repo / raw).resolve()
        record["_resolved_path"] = raw
        record.setdefault("id", f"ART-{index:03d}")
        record.setdefault("filename", raw.name)
        normalized.append(record)
    return normalized, source_path


def _relative_runtime_path(value: str | Path) -> str:
    return Path(value).as_posix().lstrip("./")


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False


def writable_path_errors(path: str | Path, workspace_root: str | Path) -> list[str]:
    """Return errors if a generated artifact is outside the sole write root."""
    target = Path(path)
    root = Path(workspace_root)
    errors: list[str] = []
    if not _is_within(target, root):
        errors.append("generated artifact path is outside clean-room workspace")
    if target.resolve() == root.resolve():
        errors.append("generated artifact path must name a file or child directory")
    return errors


def validate_generated_path(path: str | Path, workspace_root: str | Path) -> bool:
    return not writable_path_errors(path, workspace_root)


def _iter_visible_files(root: Path) -> tuple[list[str], list[str]]:
    visible: list[str] = []
    forbidden: list[str] = []
    for current, directories, filenames in os.walk(root, followlinks=False):
        current_path = Path(current)
        for name in list(directories):
            candidate = current_path / name
            relative = candidate.relative_to(root).as_posix()
            if candidate.is_symlink():
                forbidden.append(f"symlink:{relative}")
                directories.remove(name)
                continue
            parts = {part.lower() for part in Path(relative).parts}
            if parts & FORBIDDEN_PARTS or _forbidden_name(relative, name):
                forbidden.append(relative)
        for name in filenames:
            candidate = current_path / name
            relative = candidate.relative_to(root).as_posix()
            visible.append(relative)
            if candidate.is_symlink():
                forbidden.append(f"symlink:{relative}")
                continue
            parts = {part.lower() for part in Path(relative).parts}
            if parts & FORBIDDEN_PARTS or _forbidden_name(relative, name):
                forbidden.append(relative)
    return sorted(visible), sorted(set(forbidden))


def _forbidden_name(relative: str, name: str) -> bool:
    # Evaluation/reference prose is legitimate inside the trusted Skill
    # itself; evaluator-like filenames outside that subtree are not.
    if name.lower() in ALWAYS_FORBIDDEN_FILENAMES:
        return True
    if Path(relative).parts[:1] == ("skill",):
        return False
    if any(pattern.search(name) for pattern in FORBIDDEN_NAME_PATTERNS):
        return True
    if Path(relative).parts[:1] != ("skill",):
        lowered = name.lower()
        if any(token in lowered for token in ("evaluation", "postmortem", "rubric", "known_failure", "known-failure")):
            return True
    return False


def _scan_content(root: Path, visible_paths: Iterable[str]) -> list[str]:
    findings: list[str] = []
    for relative in visible_paths:
        path = root / relative
        if path.suffix.lower() not in TEXT_SUFFIXES or path.is_symlink():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                text = path.read_text(encoding="cp936")
            except (OSError, UnicodeError):
                continue
        except OSError:
            continue
        for marker in CONTENT_MARKERS:
            if marker.search(text):
                findings.append(f"{relative}:{marker.pattern}")
    return sorted(set(findings))


def scan_visibility(root: str | Path, run_id: str) -> dict[str, Any]:
    """Scan every model-visible path and text file before launch."""
    root_path = Path(root).resolve()
    if not root_path.is_dir():
        raise CleanRoomError(f"clean-room root does not exist: {root_path}")
    visible, forbidden = _iter_visible_files(root_path)
    for relative in visible:
        for part in Path(relative).parts:
            if re.fullmatch(r"run-(?:001|002|003)", part, re.IGNORECASE):
                forbidden.append(relative)
    for current, directories, _filenames in os.walk(root_path, followlinks=False):
        current_path = Path(current)
        for name in directories:
            if re.fullmatch(r"run-(?:001|002|003)", name, re.IGNORECASE):
                forbidden.append((current_path / name).relative_to(root_path).as_posix())
    leakage = _scan_content(root_path, visible)
    forbidden.extend(leakage)
    report = {
        "schema_version": 1,
        "run_id": run_id,
        "visible_file_count": len(visible),
        "visible_paths": visible,
        "forbidden_matches": sorted(set(forbidden)),
        "content_leakage_matches": leakage,
        "status": "PASS" if not forbidden else "CLEAN_ROOM_FAIL",
    }
    return report


def _write_yaml(path: Path, data: Mapping[str, Any]) -> None:
    path.write_text(yaml.safe_dump(dict(data), allow_unicode=True, sort_keys=False), encoding="utf-8")


def _ensure_outside_repo(output_root: Path, developer_repo: Path) -> None:
    if _is_within(output_root, developer_repo):
        raise CleanRoomError("clean-room root must be outside the developer repository")


def _detect_skill_version(skill_file: Path) -> str:
    try:
        text = skill_file.read_text(encoding="utf-8")
        if text.startswith("---"):
            frontmatter = text.split("---", 2)[1]
            data = yaml.safe_load(frontmatter)
            if isinstance(data, Mapping):
                metadata = data.get("metadata")
                if isinstance(metadata, Mapping) and metadata.get("version"):
                    return str(metadata["version"])
    except (OSError, UnicodeError, yaml.YAMLError):
        pass
    return "UNSPECIFIED"


def prepare_clean_room(
    developer_repo: str | Path,
    benchmark_id: str,
    run_id: str,
    problem_source: str | Path | Mapping[str, Any] | Sequence[Any],
    *,
    output_root: str | Path | None = None,
    skill_version: str = "UNSPECIFIED",
    use_hardlinks: bool = True,
) -> CleanRoomResult:
    """Create a fresh clean-room bundle and fail closed on visibility findings."""
    repo = Path(developer_repo).resolve()
    if not repo.is_dir():
        raise CleanRoomError(f"developer repository does not exist: {repo}")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", benchmark_id):
        raise ValueError("benchmark_id contains unsupported path characters")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", run_id):
        raise ValueError("run_id contains unsupported path characters")
    if output_root is None:
        root = Path(tempfile.gettempdir()) / "huawei-cup-benchmark" / run_id
    else:
        root = Path(output_root).resolve()
    _ensure_outside_repo(root, repo)
    if root.exists():
        raise CleanRoomError(f"clean-room destination already exists: {root}")

    source_artifacts, _source_record = _load_source_record(problem_source, repo)
    skill_source = repo / "skill"
    if not skill_source.is_dir():
        raise CleanRoomError(f"runtime skill directory does not exist: {skill_source}")
    root.mkdir(parents=True)
    for directory in ("input", "workspace", "workspace/code", "workspace/outputs", "workspace/experiments", "workspace/evidence", "workspace/paper"):
        (root / directory).mkdir(parents=True, exist_ok=False)
    try:
        for source in sorted(skill_source.rglob("*")):
            if source.is_file() and not source.is_symlink() and "__pycache__" not in source.parts:
                destination = root / "skill" / source.relative_to(skill_source)
                _copy_file(source, destination, use_hardlinks=False)
        input_records: list[dict[str, Any]] = []
        for artifact in source_artifacts:
            source = Path(artifact["_resolved_path"])
            if not source.is_file() or source.is_symlink():
                raise CleanRoomError(f"source artifact is not a regular file: {source}")
            canonical_hash = str(artifact.get("sha256", "")).lower().strip()
            if not re.fullmatch(r"[0-9a-f]{64}", canonical_hash):
                raise CleanRoomError(f"source artifact {artifact.get('id')} has no valid canonical SHA256")
            actual_canonical_hash = sha256(source)
            if actual_canonical_hash != canonical_hash:
                raise CleanRoomError(
                    f"canonical source hash mismatch for {source.name}: expected {canonical_hash}, got {actual_canonical_hash}"
                )
            filename = Path(str(artifact.get("filename") or source.name)).name
            destination = root / "input" / filename
            method = _copy_file(source, destination, use_hardlinks=use_hardlinks)
            runtime_hash = sha256(destination)
            if runtime_hash != actual_canonical_hash:
                raise CleanRoomError(f"runtime input hash mismatch for {filename}")
            input_records.append({
                "source_artifact_id": str(artifact.get("id")),
                "clean_room_path": _relative_runtime_path(destination.relative_to(root)),
                "canonical_sha256": actual_canonical_hash,
                "runtime_sha256": runtime_hash,
                "transfer": method,
            })

        active_evidence = {
            "schema_version": 1,
            "active_run_id": run_id,
            "active_evidence_set": {},
        }
        _write_yaml(root / "workspace/evidence/active-evidence-set.yaml", active_evidence)
        workspace_manifest = {
            "schema_version": 1,
            "run_id": run_id,
            "benchmark_id": benchmark_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "active_run_id": run_id,
            "isolation_mode": "clean_room",
            "immutable_inputs": [
                {"path": item["clean_room_path"], "sha256": item["runtime_sha256"]}
                for item in input_records
            ],
            "writable_root": "workspace",
            "allowed_write_root": "workspace",
                "allowed_read_roots": ["input", "skill"],
            "prior_run_artifacts_visible": False,
            "developer_repository_visible": False,
            "evaluator_files_visible": False,
        }
        _write_yaml(root / "workspace/workspace-manifest.yaml", workspace_manifest)

        skill_files = _runtime_skill_files(root / "skill")
        canonical_skill_hash = _hash_files(skill_source, _runtime_skill_files(skill_source))
        runtime_skill_hash = _hash_files(root / "skill", skill_files)
        if runtime_skill_hash != canonical_skill_hash:
            raise CleanRoomError("runtime Skill hash does not match the developer source Skill")
        resolved_skill_version = skill_version if skill_version != "UNSPECIFIED" else _detect_skill_version(skill_source / "SKILL.md")
        manifest = {
            "schema_version": 1,
            "run_id": run_id,
            "benchmark_id": benchmark_id,
            "skill_version": resolved_skill_version,
            "skill_hash": runtime_skill_hash,
            "canonical_skill_hash": canonical_skill_hash,
            "runtime_allowlist": {
                "skill": [path.relative_to(root).as_posix() for path in sorted(skill_files)],
                "templates": [],
                "scripts": [],
                "support": [],
            },
            "input_artifacts": input_records,
            "model_visible_root": ".",
            "writable_root": "workspace",
            "developer_repository_visible": False,
            "prior_runs_visible": False,
            "evaluator_files_visible": False,
            "visibility_scan": {"status": "PENDING"},
        }
        _write_yaml(root / "clean-room-manifest.yaml", manifest)
        report = scan_visibility(root, run_id)
        _write_yaml(root / "visibility-report.yaml", report)
        manifest["visibility_scan"] = {
            "status": report["status"],
            "visible_file_count": report["visible_file_count"],
            "forbidden_matches": report["forbidden_matches"],
        }
        _write_yaml(root / "clean-room-manifest.yaml", manifest)
        if report["status"] != "PASS":
            raise CleanRoomError("clean-room visibility scan failed: " + ", ".join(report["forbidden_matches"]))
        return CleanRoomResult(root, root / "clean-room-manifest.yaml", root / "visibility-report.yaml")
    except Exception:
        shutil.rmtree(root, ignore_errors=True)
        raise


def canonicalize_clean_room(
    clean_room_root: str | Path,
    archive_root: str | Path,
    paths: Iterable[str | Path] | None = None,
    *,
    remove: bool = True,
) -> Path:
    """Copy selected runtime outputs to an archive and optionally remove the room."""
    root = Path(clean_room_root).resolve()
    archive = Path(archive_root).resolve()
    if not root.is_dir():
        raise CleanRoomError(f"clean-room root does not exist: {root}")
    marker = root / "clean-room-manifest.yaml"
    if not marker.is_file():
        raise CleanRoomError("refusing canonicalization or cleanup without clean-room-manifest.yaml")
    if archive.exists():
        raise CleanRoomError(f"archive destination already exists: {archive}")
    if _is_within(archive, root):
        raise CleanRoomError("archive destination must be outside the clean room")
    selected = list(paths) if paths is not None else ["clean-room-manifest.yaml", "visibility-report.yaml", "workspace"]
    archive.mkdir(parents=True)
    copied: list[dict[str, Any]] = []
    try:
        for value in selected:
            relative = Path(value)
            source = (root / relative).resolve()
            if not _is_within(source, root) or not source.exists():
                raise CleanRoomError(f"canonicalization path is missing or outside clean room: {value}")
            destination = archive / relative
            if source.is_dir():
                for file in sorted(source.rglob("*")):
                    if file.is_file() and not file.is_symlink():
                        rel_file = file.relative_to(root)
                        target = archive / rel_file
                        _copy_file(file, target, use_hardlinks=False)
                        copied.append({"path": rel_file.as_posix(), "sha256": sha256(target)})
            elif source.is_file() and not source.is_symlink():
                _copy_file(source, destination, use_hardlinks=False)
                copied.append({"path": relative.as_posix(), "sha256": sha256(destination)})
            else:
                raise CleanRoomError(f"cannot canonicalize symlink or special file: {value}")
        _write_yaml(
            archive / "canonicalization-manifest.yaml",
            {
                "schema_version": 1,
                "source_root": "clean-room-runtime",
                "selected_paths": [_relative_runtime_path(item) for item in selected],
                "artifacts": copied,
                "clean_room_removed": remove,
            },
        )
    except Exception:
        shutil.rmtree(archive, ignore_errors=True)
        raise
    if remove:
        shutil.rmtree(root)
    return archive


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--developer-repo", type=Path, required=True)
    parser.add_argument("--benchmark-id", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--problem-source", type=Path, required=True)
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--skill-version", default="UNSPECIFIED")
    parser.add_argument("--copy-inputs", action="store_true", help="force copy instead of hard-link where supported")
    args = parser.parse_args()
    result = prepare_clean_room(
        args.developer_repo,
        args.benchmark_id,
        args.run_id,
        args.problem_source,
        output_root=args.output_root,
        skill_version=args.skill_version,
        use_hardlinks=not args.copy_inputs,
    )
    print(json.dumps({
        "clean_room": str(result.root),
        "manifest": str(result.manifest_path),
        "visibility_report": str(result.visibility_report_path),
        "status": "READY_FOR_MODEL",
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
