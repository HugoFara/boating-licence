"""Tests for the upstream-staleness diff (`src/staleness.py`).

The diff is the part with logic worth pinning: given a blessed lock and a current
snapshot, it must classify each source as added / removed / changed, say *what*
moved (version vs content), and grade the change so CI fails only on law drift.
The fingerprinting itself (hashing cached bytes) is exercised end-to-end by
`python run.py check-sources --offline`; here we keep it offline and synthetic.

Run with `python tests/test_staleness.py`.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import staleness                                        # noqa: E402


def _fp(grade="law", version="v1", digest="aaaa"):
    return {"kind": "fedlex", "grade": grade,
            "legal_version": version, "digest": digest}


def test_unchanged_yields_no_changes():
    lock = {"oni": _fp(), "wp": _fp(grade="reference")}
    assert staleness.diff(lock, dict(lock)) == []


def test_content_change_is_flagged_law_grade():
    lock = {"oni": _fp(version="2022-01-01", digest="aaaa")}
    cur = {"oni": _fp(version="2022-01-01", digest="bbbb")}    # same version, new bytes
    [c] = staleness.diff(lock, cur)
    assert c["status"] == "changed" and c["grade"] == "law"
    assert c["what"] == "content"                              # digest moved, version didn't


def test_version_and_content_change_reports_both():
    lock = {"oni": _fp(version="2022-01-01", digest="aaaa")}
    cur = {"oni": _fp(version="2025-06-01", digest="bbbb")}
    [c] = staleness.diff(lock, cur)
    assert c["what"] == "version, content"
    assert c["version"] == ("2022-01-01", "2025-06-01")


def test_added_and_removed():
    lock = {"gone": _fp()}
    cur = {"fresh": _fp(grade="reference")}
    by_id = {c["id"]: c for c in staleness.diff(lock, cur)}
    assert by_id["gone"]["status"] == "removed"
    assert by_id["fresh"]["status"] == "added"


def test_significant_only_when_law_grade_drifts():
    # A reference (Wikipedia/HTML prose) change must not fail CI; a law change must.
    ref_only = staleness.diff({"wp": _fp(grade="reference", digest="a")},
                              {"wp": _fp(grade="reference", digest="b")})
    assert ref_only and not any(c["grade"] == "law" for c in ref_only)

    law = staleness.diff({"oni": _fp(digest="a")}, {"oni": _fp(digest="b")})
    assert any(c["grade"] == "law" for c in law)


def test_report_is_clean_message_when_empty():
    assert "no upstream drift" in staleness.format_report([])


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
