"""Contract tests for the Phase-2 question schema (`src/questions`).

Plain asserts, no test framework — run with `python tests/test_questions.py`.
These pin the locked decisions (multi-select answers, point-based scoring at the
official 165/180 threshold, the review-status export gate, provenance round-trip)
so the downstream generators can rely on a stable shape.
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.questions import (Question, Choice, Provenance, ExamConfig,  # noqa: E402
    make_question_id, validate, score, grade_exam, grade_exam_blocks,
    connect, write_questions, set_meta, export_json, load_questions,
    shuffle_choices)


def _prov(unit_id="u", ref="r"):
    return Provenance(unit_id=unit_id, ref=ref, source="ONI", url="https://x",
                      as_of="2022-01-01", licence="Public domain")


def _rule_q(qid, correct=(0,)):
    return Question(
        id=qid, theme="lois", kind="rule_mc", stem="s",
        choices=[Choice("a", is_correct=0 in correct),
                 Choice("b", is_correct=1 in correct),
                 Choice("c", is_correct=2 in correct)],
        provenance=_prov())


def test_validation():
    ok = _rule_q("q-ok", correct=(0,))
    assert validate(ok) == [], validate(ok)
    # two correct is legal (multi-select)
    assert validate(_rule_q("q-2", correct=(0, 1))) == []
    # zero correct, all correct, and missing provenance are rejected
    assert validate(_rule_q("q-0", correct=())) , "0-correct must fail"
    assert validate(_rule_q("q-3", correct=(0, 1, 2))), "all-correct must fail"
    fig = Question(id="q-f", theme="signalisation", kind="figure_recognition",
                   stem="?", choices=[Choice("a", is_correct=True), Choice("b")],
                   provenance=_prov())
    assert any("no image" in e for e in validate(fig)), "figure w/o image must fail"


def test_correct_property():
    assert _rule_q("q", correct=(0,)).correct == [0]
    assert _rule_q("q", correct=(0, 1)).correct == [0, 1]


def test_scoring_all_or_nothing():
    assert score([0], [0], 3, 3, "all_or_nothing") == 3.0
    assert score([1], [0], 3, 3, "all_or_nothing") == 0.0
    assert score([0, 1], [0, 1], 3, 3, "all_or_nothing") == 3.0
    assert score([0], [0, 1], 3, 3, "all_or_nothing") == 0.0   # partial miss = 0


def test_scoring_partial():
    assert score([0], [0, 1], 3, 3, "partial") == 2.0          # 2/3 judgments right
    assert score([0, 1], [0, 1], 3, 3, "partial") == 3.0


def test_pass_boundary():
    """Official: 165/180 passes; that is at most 15 fault points = 5 wrong q."""
    cfg = ExamConfig()
    qs = [_rule_q(f"q{i}", correct=(0,)) for i in range(60)]
    five_wrong = {f"q{i}": ([0] if i >= 5 else [1]) for i in range(60)}
    six_wrong = {f"q{i}": ([0] if i >= 6 else [1]) for i in range(60)}
    r5 = grade_exam(qs, five_wrong, cfg)
    r6 = grade_exam(qs, six_wrong, cfg)
    assert r5 == {"earned": 165.0, "total": 180, "pass_points": 165,
                  "fault_points": 15.0, "passed": True}, r5
    assert r6["passed"] is False and r6["earned"] == 162.0, r6


def _blk_q(qid, block, correct_first=True):
    """A 2-option block-tagged question; first option correct unless told otherwise."""
    return Question(id=qid, theme="lois", kind="official_mc", stem="s", block=block,
                    choices=[Choice("a", is_correct=correct_first),
                             Choice("b", is_correct=not correct_first)],
                    provenance=_prov())


def test_block_grading_passes_when_every_block_meets_minimum():
    # SBF-See shape: 7 Basis (need ≥5) + 23 spezifisch (need ≥18).
    qs = ([_blk_q(f"b{i}", "basis") for i in range(7)]
          + [_blk_q(f"s{i}", "spezifisch_see") for i in range(23)])
    answers = {q.id: [0] for q in qs}                 # all correct (option a)
    res = grade_exam_blocks(qs, answers,
                            [("basis", 5), ("spezifisch_see", 18)])
    assert res["passed"] is True
    assert {b["block"]: b["correct"] for b in res["blocks"]} == \
        {"basis": 7, "spezifisch_see": 23}


def test_block_grading_fails_when_one_block_short_despite_high_total():
    # Ace every spezifisch question but flunk Basis (only 3/7 right < 5) — the
    # grand total is high, yet a short block must still fail the sitting.
    qs = ([_blk_q(f"b{i}", "basis") for i in range(7)]
          + [_blk_q(f"s{i}", "spezifisch_see") for i in range(23)])
    answers = {q.id: [0] for q in qs}
    for i in range(4):                                # 4 Basis answered wrong
        answers[f"b{i}"] = [1]
    res = grade_exam_blocks(qs, answers,
                            [("basis", 5), ("spezifisch_see", 18)])
    assert res["total_correct"] == 26 and res["total_questions"] == 30
    assert res["passed"] is False
    basis = [b for b in res["blocks"] if b["block"] == "basis"][0]
    assert basis["correct"] == 3 and basis["passed"] is False


def test_block_grading_pass_total_for_no_minimum_permits():
    # SBF-Binnen-Segeln: blocks have no standalone minimum (min_correct 0) but the
    # sitting needs ≥20/25 overall — `pass_total` enforces that.
    qs = [_blk_q(f"q{i}", "basis") for i in range(25)]
    answers = {q.id: [0] for q in qs}
    for i in range(6):                                # 19/25 correct → below 20
        answers[f"q{i}"] = [1]
    blocks = [("basis", 0)]
    assert grade_exam_blocks(qs, answers, blocks, pass_total=20)["passed"] is False
    answers["q0"] = [0]                               # back to 20/25 → passes
    assert grade_exam_blocks(qs, answers, blocks, pass_total=20)["passed"] is True


def test_persistence_and_export_gate():
    db, js = "data/_qtest.sqlite", "data/_qtest.json"
    for f in (db, js):
        if os.path.exists(f):
            os.remove(f)
    try:
        approved = _rule_q("q-app", correct=(0, 1))
        approved.review_status = "approved"
        auto = _rule_q("q-auto", correct=(0,))
        auto.review_status = "auto_approved"
        pending = _rule_q("q-pend", correct=(0,))   # LLM draft — must not export
        pending.review_status = "pending"
        conn = connect(db)
        set_meta(conn, schema="v1")
        write_questions(conn, [approved, auto, pending])
        n = export_json(conn, js, exportable_only=True)
        data = json.load(open(js))
        assert n == 2, n
        ids = {q["id"] for q in data["questions"]}
        assert ids == {"q-app", "q-auto"}, ids
        # multi-select answer survives the round trip
        back = {q.id: q for q in load_questions(conn)}
        assert back["q-app"].correct == [0, 1]
        assert len(back) == 3
        conn.close()
    finally:
        for f in (db, js):
            if os.path.exists(f):
                os.remove(f)


def test_export_display_shuffle():
    # Generators emit the keyed option first; the export must permute choice
    # positions so "answer A" is not a tell — deterministically (seeded by id),
    # keeping `correct` aligned with the shuffled flags, permuting (never
    # rewriting) option content, and leaving the DB in canonical authored order
    # (the Anki/GIFT round-trip matches by position).
    db, js = "data/_qtest_shuffle.sqlite", "data/_qtest_shuffle.json"
    for f in (db, js):
        if os.path.exists(f):
            os.remove(f)
    try:
        qs = []
        for i in range(24):
            q = _rule_q(f"q-shuf{i:02d}", correct=(0,) if i % 4 else (0, 1))
            q.review_status = "auto_approved"
            qs.append(q)
        conn = connect(db)
        set_meta(conn, schema="v1")
        write_questions(conn, qs)
        export_json(conn, js, exportable_only=True)
        first = open(js, encoding="utf-8").read()
        export_json(conn, js, exportable_only=True)
        assert first == open(js, encoding="utf-8").read(), "shuffle must be deterministic"
        moved = 0
        for qd in json.loads(first)["questions"]:
            flags = [i for i, c in enumerate(qd["choices"]) if c["is_correct"]]
            assert qd["correct"] == flags, "correct must index the SHUFFLED choices"
            assert sorted(c["text"] for c in qd["choices"]) == ["a", "b", "c"], \
                "options must be permuted, not rewritten"
            if flags != [0]:
                moved += 1
        assert moved, "shuffle should move answers off position 0"
        # the bank keeps the canonical authored order (keyed option first)
        assert all(0 in q.correct for q in load_questions(conn))
        conn.close()
    finally:
        for f in (db, js):
            if os.path.exists(f):
                os.remove(f)


def test_shuffle_choices_in_place_pure_permutation():
    q = _rule_q("q-perm", correct=(1,))
    before = [(c.text, c.is_correct) for c in q.choices]
    shuffle_choices(q)
    assert sorted((c.text, c.is_correct) for c in q.choices) == sorted(before)
    assert q.correct == [i for i, c in enumerate(q.choices) if c.is_correct]
    again = _rule_q("q-perm", correct=(1,))
    shuffle_choices(again)
    assert [c.text for c in again.choices] == [c.text for c in q.choices], \
        "same id → same permutation"


def test_invalid_batch_rejected():
    db = "data/_qtest2.sqlite"
    if os.path.exists(db):
        os.remove(db)
    try:
        conn = connect(db)
        try:
            write_questions(conn, [_rule_q("q-bad", correct=())])
            assert False, "write_questions must reject an invalid question"
        except ValueError as e:
            assert "invalid question" in str(e)
        conn.close()
    finally:
        if os.path.exists(db):
            os.remove(db)


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"\n{len(tests)} tests passed")
