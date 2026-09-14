"""Package one developer repository under a single huawei-cup-2026/ root."""

from __future__ import annotations

import argparse
import os
import zipfile
from pathlib import Path, PurePosixPath


TOP_LEVEL = "huawei-cup-2026"
EXCLUDED_DIRS = {".git", "dist", "artifacts", ".pytest_cache", "__pycache__", ".tmp", ".cache", ".venv", "venv"}
EXCLUDED_ROOT_DIRS = {"outputs", "output", "work", ".runtime", "tmp", "temp", "debug", "scratch"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def validate_repository_zip(path: str | Path) -> list[str]:
    errors: list[str] = []
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if not names or {PurePosixPath(name).parts[0] for name in names} != {TOP_LEVEL}:
            errors.append("distribution must have exactly one huawei-cup-2026/ top level")
        if len(names) != len(set(names)):
            errors.append("duplicate archive entry")
        for name in names:
            path = PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts or "\\" in name:
                errors.append(f"non-portable archive path: {name}")
            if set(path.parts) & EXCLUDED_DIRS or path.suffix.lower() in EXCLUDED_SUFFIXES:
                errors.append(f"cache or generated bundle in distribution: {name}")
            if len(path.parts) > 1 and path.parts[1] in EXCLUDED_ROOT_DIRS:
                errors.append(f"development output in distribution: {name}")
        if archive.testzip() is not None:
            errors.append("archive CRC verification failed")
    return errors


def package_repository(developer_repo: str | Path, output: str | Path) -> Path:
    repo = Path(developer_repo).resolve()
    target = Path(output).resolve()
    if not (repo / "skill/SKILL.md").is_file():
        raise ValueError("source must be the developer repository, not its parent directory")
    if target.exists():
        raise FileExistsError(target)
    artifact_root = repo / "development" / "artifacts"
    if target.is_relative_to(repo) and not target.is_relative_to(artifact_root):
        raise ValueError("repository-local distribution must be under development/artifacts/")
    target.parent.mkdir(parents=True, exist_ok=True)
    created = False
    try:
        with zipfile.ZipFile(target, "x", compression=zipfile.ZIP_DEFLATED) as archive:
            created = True
            archive.writestr(TOP_LEVEL + "/", b"")
            for current, directories, filenames in os.walk(repo, followlinks=False):
                base = Path(current)
                directories[:] = sorted(name for name in directories if name not in EXCLUDED_DIRS
                                        and not (base == repo and name in EXCLUDED_ROOT_DIRS))
                for name in directories + sorted(filenames):
                    source = base / name
                    if source.is_symlink() or bool(getattr(source, "is_junction", lambda: False)()):
                        raise ValueError(f"linked repository path is not packageable: {source}")
                    if source.suffix.lower() in EXCLUDED_SUFFIXES:
                        continue
                    relative = f"{TOP_LEVEL}/{source.relative_to(repo).as_posix()}"
                    if source.is_dir():
                        archive.writestr(relative + "/", b"")
                    elif source.is_file():
                        archive.write(source, relative)
        errors = validate_repository_zip(target)
        if errors:
            raise ValueError("; ".join(errors))
        return target
    except Exception:
        if created:
            target.unlink(missing_ok=True)
        raise


def package_skill(skill_root: str | Path, output: str | Path) -> Path:
    """Package only a self-contained Skill under one ``skill/`` top level."""
    source_root = Path(skill_root).resolve()
    target = Path(output).resolve()
    if not (source_root / "SKILL.md").is_file() or not (source_root / "routing.yaml").is_file():
        raise ValueError("source must be a self-contained Skill directory")
    if target.exists():
        raise FileExistsError(target)
    if target.is_relative_to(source_root):
        raise ValueError("Skill package output must be outside the Skill source")
    target.parent.mkdir(parents=True, exist_ok=True)
    created = False
    try:
        with zipfile.ZipFile(target, "x", compression=zipfile.ZIP_DEFLATED) as archive:
            created = True
            archive.writestr("skill/", b"")
            for current, directories, filenames in os.walk(source_root, followlinks=False):
                base = Path(current)
                directories[:] = sorted(name for name in directories if name not in EXCLUDED_DIRS)
                for name in directories + sorted(filenames):
                    source = base / name
                    if source.is_symlink() or bool(getattr(source, "is_junction", lambda: False)()):
                        raise ValueError(f"linked Skill path is not packageable: {source}")
                    if source.suffix.lower() in EXCLUDED_SUFFIXES:
                        continue
                    relative = f"skill/{source.relative_to(source_root).as_posix()}"
                    if source.is_dir():
                        archive.writestr(relative + "/", b"")
                    elif source.is_file():
                        archive.write(source, relative)
        with zipfile.ZipFile(target) as archive:
            names = archive.namelist()
            if not names or {PurePosixPath(name).parts[0] for name in names} != {"skill"}:
                raise ValueError("Skill distribution must contain only skill/")
            if archive.testzip() is not None:
                raise ValueError("Skill archive CRC verification failed")
        return target
    except Exception:
        if created:
            target.unlink(missing_ok=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--developer-repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--skill-only", action="store_true")
    args = parser.parse_args()
    target = package_skill(args.developer_repo / "skill", args.output) if args.skill_only else package_repository(args.developer_repo, args.output)
    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
