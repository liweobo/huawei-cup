"""Small archive/reader tests, not another 2017F solve."""
import copy
import pytest
from verify_benchmark import ROOT, arithmetic, check_pdf_bytes, check_review, read, snapshot_check


def test_all_reference_bytes_match():
    for entry in read("reference-manifest.json")["files"]:
        check_pdf_bytes((ROOT / entry["path"]).read_bytes(), entry)


def test_hash_tamper_is_rejected():
    entry = dict(read("reference-manifest.json")["files"][0], sha256="0" * 64)
    with pytest.raises(AssertionError):
        check_pdf_bytes((ROOT / entry["path"]).read_bytes(), entry)


def test_review_counts_match_original_extraction():
    check_review(read("review-audit.json"), read("extraction-audit.json"))


def test_unread_page_claim_is_rejected():
    audit = copy.deepcopy(read("review-audit.json"))
    audit["files"][0]["text_pages_read"] = [1, 5]
    with pytest.raises(AssertionError):
        check_review(audit, read("extraction-audit.json"))


def test_printed_arithmetic_only():
    result = arithmetic()
    assert result["status"] == "PASS"
    assert result["FK0263_p22_park2_single_trip_departures"] == 89


def test_frozen_history_and_summary_unchanged():
    assert snapshot_check()["head"] == "33548fd4a53ec3b05d4fc0d19cb9cdc319e8a8bc"
