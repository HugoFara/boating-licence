"""Tests for the durable review ledger (`src/questions/seed_review.py`): record
merges and keeps only approve/reject, and apply() restores a rebuilt bank's
manual decisions exactly — the guarantee that the published bank is reproducible
from committed inputs after the regenerable questions.sqlite is wiped.

Run with `python tests/test_seed_review.py`.
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.questions import schema as qschema, seed_review  # noqa: E402
from src.questions.schema import Question, Choice, Provenance  # noqa: E402


def _q(qid, status="pending"):
    return Question(
        id=qid, theme="lois", kind="rule_mc", stem=f"stem {qid}?", lang="fr",
        choices=[Choice("a", None, True), Choice("b", None, False),
                 Choice("c", None, False)],
        polarity="affirmative", image=None, points=3, explanation="",
        review_status=status, distractor_strategy="curated",
        generator="seed:curated.v1",
        provenance=Provenance("u-1", "ONI art. 1", "ONI", "https://x",
                              "2020-01-01", "Public domain"))


def _with_temp_ledger(fn):
    """Run fn with seed_review.LEDGER pointed at a throwaway file."""
    orig = seed_review.LEDGER
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    os.remove(path)                      # start absent, like a fresh repo
    seed_review.LEDGER = path
    try:
        fn()
    finally:
        seed_review.LEDGER = orig
        if os.path.exists(path):
            os.remove(path)


def test_record_keeps_only_decisions():
    def body():
        assert seed_review.load() == {}          # absent -> empty
        led = seed_review.record({"a": "approved", "b": "rejected",
                                  "c": "pending", "d": "bogus"})
        assert led == {"a": "approved", "b": "rejected"}   # pending/bogus dropped
        led = seed_review.record({"a": "rejected", "e": "approved"})  # merge + update
        assert led == {"a": "rejected", "b": "rejected", "e": "approved"}
    _with_temp_ledger(body)


def test_apply_restores_after_rebuild():
    def body():
        fd, db = tempfile.mkstemp(suffix=".sqlite")
        os.close(fd)
        try:
            conn = qschema.connect(db)
            # bank rebuilt: seed questions land as PENDING
            qschema.write_questions(conn, [_q("q-keep"), _q("q-drop"), _q("q-other")])
            seed_review.record({"q-keep": "approved", "q-drop": "rejected"})

            out = seed_review.apply(conn)
            assert out == {"approved": 1, "rejected": 1}
            got = {x.id: x.review_status for x in qschema.load_questions(conn)}
            assert got["q-keep"] == "approved"
            assert got["q-drop"] == "rejected"
            assert got["q-other"] == "pending"      # untouched
            # an id in the ledger but absent from the bank updates nothing
            seed_review.record({"q-missing": "approved"})
            assert seed_review.apply(conn)["approved"] == 1
            conn.close()
        finally:
            os.remove(db)
    _with_temp_ledger(body)


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"\n{len(tests)} tests passed")
