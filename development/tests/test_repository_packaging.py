from pathlib import Path
import zipfile

import pytest

from development.tooling.package_repository import package_repository, package_skill, validate_repository_zip


def test_single_top_level_and_cache_exclusion(tmp_path: Path) -> None:
    repo = tmp_path / "huawei-cup-2026"
    for relative in ("skill/SKILL.md", "benchmarks/runs/run-003/evaluation.yaml",
                     "benchmarks/runs/run-003/outputs/metrics.json", ".pytest_cache/state", "scripts/__pycache__/a.pyc",
                     "skill/stale.pyo", "dist/previous.zip", "outputs/debug.txt"):
        path = repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("fixture", encoding="utf-8")
    sibling = tmp_path / "benchmarks/runs/run-003/evaluation.yaml"
    sibling.parent.mkdir(parents=True)
    sibling.write_text("fixture", encoding="utf-8")
    output = package_repository(repo, tmp_path / "distribution.zip")
    assert validate_repository_zip(output) == []
    with zipfile.ZipFile(output) as archive:
        names = archive.namelist()
    assert {name.split("/")[0] for name in names} == {"huawei-cup-2026"}
    assert len([name for name in names if name.endswith("run-003/evaluation.yaml")]) == 1
    assert "huawei-cup-2026/benchmarks/runs/run-003/outputs/metrics.json" in names
    assert not any(token in name for name in names for token in ("__pycache__", ".pytest_cache", ".pyc", ".pyo", "/dist/", "outputs/debug"))


def test_parent_workspace_cannot_be_packaged(tmp_path: Path) -> None:
    (tmp_path / "huawei-cup-2026/skill").mkdir(parents=True)
    (tmp_path / "huawei-cup-2026/skill/SKILL.md").write_text("fixture", encoding="utf-8")
    with pytest.raises(ValueError, match="parent"):
        package_repository(tmp_path, tmp_path / "bad.zip")


@pytest.mark.parametrize("entry", ["benchmarks/run-003/evaluation.yaml", "outputs/debug.txt", ".pytest_cache/state"])
def test_bad_distribution_top_level_fails(tmp_path: Path, entry: str) -> None:
    target = tmp_path / "bad.zip"
    with zipfile.ZipFile(target, "w") as archive:
        archive.writestr("huawei-cup-2026/skill/SKILL.md", "fixture")
        archive.writestr(entry, "duplicate")
    assert validate_repository_zip(target)


def test_skill_only_package_contains_no_development_assets(tmp_path: Path) -> None:
    skill = tmp_path / "skill"
    (skill / "templates").mkdir(parents=True)
    (skill / "SKILL.md").write_text("fixture", encoding="utf-8")
    (skill / "routing.yaml").write_text("version: 1\nroutes: {}\n", encoding="utf-8")
    (skill / "templates/task-anchor.md").write_text("fixture", encoding="utf-8")
    output = package_skill(skill, tmp_path / "skill-only.zip")
    with zipfile.ZipFile(output) as archive:
        names = archive.namelist()
    assert {name.split("/")[0] for name in names} == {"skill"}
    assert "skill/SKILL.md" in names
