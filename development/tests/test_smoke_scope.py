"""Live documentation defects fail without treating frozen evidence as drafts."""

from pathlib import Path
import sys

import pytest

from development.harness import router

# The harness also supports direct invocation from its own directory.
sys.modules.setdefault("router", router)
from development.harness import smoke_test


def write(root: Path, relative: str, content: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


@pytest.mark.parametrize("relative", [
    "README.md", "AGENTS.md", "skill/SKILL.md",
    "skill/workflows/validate-model.md", "skill/references/index.md",
    "skill/rules/modeling.md", "development/README.md",
    "development/docs/release-readiness.md", "development/benchmarks/README.md",
    "development/benchmarks/problems/README.md",
    "development/docs/runs/README.md", "skill/references/run-attempts/README.md",
])
def test_broken_live_link_fails(tmp_path: Path, relative: str) -> None:
    path = write(tmp_path, relative, "# Live document\n\n[resource](missing.md)\n")
    errors: list[str] = []
    assert path in smoke_test.check_live_markdown(tmp_path, errors)
    assert any("broken markdown link" in error for error in errors)
    write(path.parent, "missing.md", "# Recovered resource\n")
    errors.clear()
    smoke_test.check_live_markdown(tmp_path, errors)
    assert errors == []


@pytest.mark.parametrize("archive", ["runs", "run-attempts"])
def test_frozen_content_is_not_live_smoke(tmp_path: Path, archive: str) -> None:
    # Covers archived reports, nested evidence, and attempts, including broken
    # historical links, unfinished wording, and duplicated generated content.
    paragraph = "Retained historical evidence must keep its original bytes. " * 4
    content = f"# Frozen\n\nPLACEHOLDER\n\n[old local path](missing.md)\n\n{paragraph}\n"
    paths = [write(tmp_path, f"development/benchmarks/{archive}/{part}", content)
             for part in ("case/REPORT.md", "case/nested/validation.md")]
    before = {path: path.read_bytes() for path in paths}
    live = write(tmp_path, "README.md", "# Active overview\n")
    errors: list[str] = []
    assert smoke_test.check_live_markdown(tmp_path, errors) == [live]
    assert errors == []
    assert {path: path.read_bytes() for path in paths} == before

    # Links originating in active docs still require a real frozen target.
    live.write_text(f"[missing evidence](development/benchmarks/{archive}/absent.md)\n", encoding="utf-8")
    smoke_test.check_live_markdown(tmp_path, errors)
    assert any("broken markdown link" in error for error in errors)


@pytest.mark.parametrize("content, finding", [
    ("", "empty markdown"),
    ("# Draft\n\nTODO\n", "unfinished placeholder"),
    ("# Duplicated\n", "duplicate markdown content"),
    ("A substantive shared paragraph retains the existing live duplication check. " * 4,
     "duplicate long paragraph"),
])
def test_other_live_defects_still_fail(tmp_path: Path, content: str, finding: str) -> None:
    write(tmp_path, "development/docs/a.md", content)
    write(tmp_path, "development/docs/b.md", content)
    errors: list[str] = []
    smoke_test.check_live_markdown(tmp_path, errors)
    assert any(finding in error for error in errors)


def test_markdown_findings_propagate_to_cli_status(monkeypatch, capsys) -> None:
    def broken_document(root, errors):
        errors.append("broken markdown link README.md -> missing.md")
        return []

    monkeypatch.setattr(smoke_test, "check_live_markdown", broken_document)
    assert smoke_test.main() == 1
    assert "broken markdown link README.md" in capsys.readouterr().out
