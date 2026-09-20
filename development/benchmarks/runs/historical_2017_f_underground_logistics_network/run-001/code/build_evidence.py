"""Seal a curated run archive; exclude raw extraction and noisy failure caches."""
import ast
import hashlib
import json
import sys
from pathlib import Path
import yaml

RUN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN.parents[4]))
from skill.scripts.runtime_provenance import validate_active_evidence_set, validate_evidence_entry, validate_experiment_record


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    (RUN / path).write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")


issues = []
for name, classification in (("default-pytest", "DEFAULT_PYTEST_ENVIRONMENT_ISSUE_EXISTING"),
                             ("smoke_test", "EXISTING_SMOKE_FAILURES_PRESERVED")):
    path = RUN / "validation-results" / f"{name}.txt"
    lines = path.read_text(encoding="utf-8").splitlines()
    patterns = ["import file mismatch", ".tmp", "44 errors", "unfinished placeholder", "historical_2005", "historical_2020"]
    examples = []
    for pattern in patterns:
        line = next((line for line in lines if pattern in line), None)
        if line:
            examples.append(line[:1600])
    issues.append({"check": name, "classification": classification, "raw_local_log": path.relative_to(RUN).as_posix(),
                   "raw_log_sha256": digest(path), "raw_log_bytes": path.stat().st_size,
                   "representative_lines": examples, "repair_attempted": False,
                   "raw_log_commit_policy": "EXCLUDED_LOCAL_CACHE; representative evidence retained here"})
save("validation-results/existing-environment-issues.json", issues)
source = next((RUN / "source").glob("*.doc"))
ids = {source.relative_to(RUN).as_posix(): "SOURCE-DOC", "inputs/oracle.json": "INPUT-ORACLE",
       "code/run_oracle.py": "CODE-ORACLE", "code/independent_audit.py": "CODE-INDEPENDENT-AUDIT",
       "results/summary.json": "RESULT-SUMMARY", "results/baseline.json": "RESULT-BASELINE",
       "results/primary.json": "RESULT-PRIMARY", "results/small-graph-oracle.json": "RESULT-ORACLE",
       "results/independent-audit.json": "RESULT-INDEPENDENT-AUDIT"}
active = {"active_run_id": "run-001", "active_evidence_set": {
    "SYNTHETIC_VALIDATION": {"run_id": "run-001", "experiment_id": "EXP-2017F-ORACLE-001",
                             "artifact_ids": ["INPUT-ORACLE", "CODE-ORACLE", "CODE-INDEPENDENT-AUDIT", "RESULT-SUMMARY",
                                              "RESULT-BASELINE", "RESULT-PRIMARY", "RESULT-ORACLE", "RESULT-INDEPENDENT-AUDIT"],
                             "claim_scope": "SYNTHETIC_CODE_VALIDATION_ONLY; no official Q1-Q4 numeric evidence"}}}
assert not validate_active_evidence_set(active, "run-001")
(RUN / "active-evidence-set.yaml").write_text(yaml.safe_dump(active, sort_keys=False), encoding="utf-8")
excluded = {"validation-results/default-pytest.txt", "validation-results/smoke_test.txt"}
indices = {"evidence-ledger.yaml", "archive-manifest.json"}
files = sorted(p for p in RUN.rglob("*") if p.is_file() and "work" not in p.relative_to(RUN).parts
               and "__pycache__" not in p.parts and p.suffix != ".pyc"
               and p.relative_to(RUN).as_posix() not in excluded | indices)
entries = []
for p in files:
    relative = p.relative_to(RUN).as_posix()
    if p.suffix == ".py":
        ast.parse(p.read_text(encoding="utf-8"))
    if p.suffix == ".json":
        json.loads(p.read_text(encoding="utf-8"))
    if p.suffix in (".yaml", ".yml"):
        yaml.safe_load(p.read_text(encoding="utf-8"))
    kind = "CODE_RUN" if relative.startswith("code/") else "EXPERIMENT_RESULT" if relative.startswith("results/") else "DOCUMENTATION"
    entry = {"artifact_id": ids.get(relative, "ART-" + hashlib.sha256(relative.encode()).hexdigest()[:14].upper()),
             "path": relative, "sha256": digest(p), "bytes": p.stat().st_size, "type": kind,
             "run_id": "run-001", "experiment_id": "EXP-2017F-ORACLE-001"}
    assert not validate_evidence_entry(entry, "run-001")
    entries.append(entry)
ledger = {"run_id": "run-001", "benchmark_id": RUN.parent.name,
          "evidence_ids": ["EVIDENCE-SYNTHETIC-001"],
          "scope": "Source/claim boundaries and synthetic evidence are distinct; no historical modeling evidence selected.",
          "index_policy": "This ledger and archive-manifest are metadata envelopes, excluded from recursive self-hashing; Git commit seals both.",
          "artifacts": entries}
(RUN / "evidence-ledger.yaml").write_text(yaml.safe_dump(ledger, sort_keys=False, allow_unicode=True), encoding="utf-8")
files.append(RUN / "evidence-ledger.yaml")
archive = {"status": "FROZEN_FOR_HUMAN_REVIEW", "files": {p.relative_to(RUN).as_posix(): digest(p) for p in files},
           "excluded": ["work/**", "__pycache__/**", *sorted(excluded)],
           "archive_manifest_self_hash": "Git commit identity; cannot embed a recursive self hash"}
save("archive-manifest.json", archive)
record = yaml.safe_load((RUN / "experiment-record.yaml").read_text(encoding="utf-8"))
assert not validate_experiment_record(record), validate_experiment_record(record)
registered = {e["artifact_id"] for e in entries}
for field in ("input_artifacts", "code_artifacts", "output_artifacts"):
    assert set(record[field]) <= registered, (field, set(record[field]) - registered)
completion = json.loads((RUN / "completion.json").read_text(encoding="utf-8"))
assert completion["final_decision"] == "BLIND_RUN_PARTIAL"
assert completion["skill_modified"] is False and completion["excellent_solutions_accessed"] is False
source_data = source.read_bytes()
assert hashlib.sha1(b"blob " + str(len(source_data)).encode() + b"\0" + source_data).hexdigest() == "c2dd56c208cf3c7f80f2e52ff1f58ee0a758166f"
extraction = json.loads((RUN / "source-provenance/extraction-audit.json").read_text(encoding="utf-8"))
assert extraction["visible_paragraph_check"]["status"] == "PASS"
assert extraction["original_image_count"] == 5 and extraction["tables"] == 0
assert "rendered_text" not in extraction, "Raw extraction text is a cache, not part of the compact audit manifest"
print(json.dumps({"evidence_gate": "PASS", "registered_artifacts": len(entries), "archive_files_including_manifest": len(files) + 1,
                  "total_bytes_without_manifest": sum(p.stat().st_size for p in files)}, indent=2))
