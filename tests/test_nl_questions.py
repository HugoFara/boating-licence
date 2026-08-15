"""Audit of the Dutch klein-vaarbewijs question bank.

These are *law-seeded* questions — authored from the ingested Dutch law because the
CBR publishes no reusable catalogue — so they get a harder audit than a verbatim
official bank would need. Four properties are checked, in rising order of how much
they can actually catch:

1. **Structure.** Three choices, at least one correct, no duplicated choice text,
   no two questions sharing a stem.
2. **Scope.** Every question hangs off an article the ministerial exam programme
   names (:mod:`countries.nl_examscope`). A question about a professional crewing
   rule is not wrong, it is simply not on this exam.
3. **Grounding.** The correct answer's content words appear in the article it
   cites — the same lexical check the drafting pipeline applies, re-run here so a
   later hand-edit cannot quietly drop below it.
4. **Numbers.** Every number a correct answer asserts appears in the article it
   cites — and, the check that actually bites, appears *beside the answer's own
   words*. Mere membership proves nothing: the BPR's definitions article runs to
   8000 characters and contains almost every small integer somewhere, so a bank
   that said a small ship is under 15 m would sail through it. This is the
   characteristic failure of a law-seeded bank — the rule says 20 m, the options
   offer 15/20/25, and one careless swap makes a wrong option the true one.

The bank is committed as `pending`; nothing here approves anything. Run with
`python tests/test_nl_questions.py`.
"""

import os
import re
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.countries import nl_examscope, nl_themes          # noqa: E402
from src.questions import prose                            # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK = os.path.join(ROOT, "data", "questions.nl.sqlite")
KB = os.path.join(ROOT, "data", "kb.nl.sqlite")
MIN_GROUNDING = 0.34


def _have() -> bool:
    return os.path.exists(BANK) and os.path.exists(KB)


def _rows():
    conn = sqlite3.connect(BANK)
    conn.row_factory = sqlite3.Row
    qs = conn.execute(
        "SELECT id, theme, stem, polarity, explanation, prov_ref, prov_unit_id "
        "FROM questions WHERE lang='nl' ORDER BY id").fetchall()
    ch = {}
    for c in conn.execute("SELECT question_id, text, is_correct FROM choices "
                          "ORDER BY question_id, idx"):
        ch.setdefault(c[0], []).append((c[1], bool(c[2])))
    kb = sqlite3.connect(KB)
    kb.row_factory = sqlite3.Row
    src = {r["id"]: r["text"] for r in kb.execute(
        "SELECT id, text FROM units WHERE lang='nl'")}
    return [dict(r) for r in qs], ch, src


def test_bank_is_present_and_non_trivial():
    if not _have():
        print("    (skipped: no Dutch bank built)")
        return
    qs, _, _ = _rows()
    assert len(qs) > 100, f"the Dutch bank is unexpectedly small: {len(qs)}"
    for q in qs:
        assert q["theme"] in nl_themes.THEMES, f"{q['id']}: theme {q['theme']!r}"


def test_every_question_is_structurally_sound():
    if not _have():
        print("    (skipped: no Dutch bank built)")
        return
    qs, ch, _ = _rows()
    seen_stems: dict[str, str] = {}
    for q in qs:
        choices = ch.get(q["id"], [])
        assert len(choices) == 3, f"{q['prov_ref']}: {len(choices)} choices"
        assert sum(1 for _, c in choices if c) >= 1, f"{q['prov_ref']}: no correct answer"
        texts = [t.strip().lower() for t, _ in choices]
        assert len(set(texts)) == 3, f"{q['prov_ref']}: duplicated choice text"
        assert q["polarity"] in ("affirmative", "negative"), q["polarity"]
        assert q["explanation"].strip(), f"{q['prov_ref']}: no explanation"
        key = q["stem"].strip().lower()
        assert key not in seen_stems, \
            f"duplicate stem: {q['prov_ref']} and {seen_stems[key]}"
        seen_stems[key] = q["prov_ref"]


def test_every_question_sits_inside_the_official_exam_programme():
    """The Dutch KB carries the professional-crewing corpus too. A question drawn
    from it would be perfectly true and completely unexaminable."""
    if not _have():
        print("    (skipped: no Dutch bank built)")
        return
    qs, _, _ = _rows()
    stray = sorted({q["prov_ref"] for q in qs
                    if not nl_examscope.examinable(q["prov_ref"])})
    assert not stray, f"outside the exam programme: {stray}"


def test_the_explanation_cites_the_article_the_question_hangs_off():
    """An explanation that names another article is either a copy-paste slip or a
    question filed against the wrong source — both invisible without this check."""
    if not _have():
        print("    (skipped: no Dutch bank built)")
        return
    qs, _, _ = _rows()
    bad = []
    for q in qs:
        m = re.search(r"Artikel\s+(\S+)$", q["prov_ref"])
        if not m:
            continue
        art = re.escape(m.group(1))
        # "BPR artikel 6.28, vierde lid" / "Wetboek van Koophandel artikel 785"
        if not re.search(rf"\b(?:artikel|art\.)\s*{art}\b", q["explanation"], re.I):
            bad.append((q["prov_ref"], q["explanation"][:60]))
    assert not bad, f"explanation cites the wrong article: {bad[:5]}"


def test_correct_answers_stay_grounded_in_their_source_article():
    if not _have():
        print("    (skipped: no Dutch bank built)")
        return
    qs, ch, src = _rows()
    weak = []
    for q in qs:
        text = src.get(q["prov_unit_id"], "")
        correct = " ".join(t for t, c in ch.get(q["id"], []) if c)
        score = prose.grounding_score(correct, text, "nl")
        if score < MIN_GROUNDING:
            weak.append((q["prov_ref"], score, correct[:50]))
    assert not weak, f"weakly grounded correct answers: {weak[:5]}"


# Numbers that carry no factual weight on their own: list markers and the
# ubiquitous "1 m" spacing between lights say nothing distinguishing.
_SKIP_NUMS = {"1", "2", "3", "4", "5"}
_NUM = re.compile(r"\b(\d+(?:[.,]\d+)?)\b")


def _numbers(s: str) -> set[str]:
    return {n.replace(",", ".") for n in _NUM.findall(s or "")} - _SKIP_NUMS


def test_every_number_in_a_correct_answer_is_in_the_law():
    """A law-seeded bank's characteristic error is a transposed value: the article
    says 20 m and the answer says 15 m. Any number a correct answer asserts must
    appear in the article it cites."""
    if not _have():
        print("    (skipped: no Dutch bank built)")
        return
    qs, ch, src = _rows()
    bad = []
    for q in qs:
        text = src.get(q["prov_unit_id"], "")
        in_law = _numbers(text)
        for t, correct in ch.get(q["id"], []):
            if not correct:
                continue
            for n in _numbers(t) - in_law:
                bad.append((q["prov_ref"], n, t[:60]))
    assert not bad, f"correct answers assert numbers the law does not: {bad[:8]}"


_WINDOW = 170          # characters either side of the number in the source


def _stated_near(source: str, number: str, answer_words: set) -> bool:
    """Does ``source`` state ``number`` in the company of the answer's own words?

    Bare membership is not enough and this is the whole point of the check: the
    BPR's definitions article runs to 8000 characters and contains almost every
    small integer somewhere, so "is 15 in the text?" is answered yes for an
    article whose actual rule is 20 m. Requiring the number to sit near the words
    the answer itself uses turns a useless test into a sharp one.
    """
    pat = re.compile(r"\b" + re.escape(number).replace(r"\.", r"[.,]") + r"\b")
    need = 1 if len(answer_words) <= 2 else 2
    for m in pat.finditer(source):
        window = source[max(0, m.start() - _WINDOW):m.end() + _WINDOW]
        if len(prose._content_words(window, "nl") & answer_words) >= need:
            return True
    return False


def test_a_number_in_a_correct_answer_is_stated_where_the_answer_says_it_is():
    """The sharpest audit in this file, and the one aimed at the characteristic
    failure of a law-seeded bank: a transposed value. The article says a small
    ship is under 20 m; offer 15/20/25 and mark 15, and every learner who read the
    law answers "wrong". Membership alone cannot catch that — a long article
    contains 15 somewhere — so the number must appear beside the answer's own
    vocabulary."""
    if not _have():
        print("    (skipped: no Dutch bank built)")
        return
    qs, ch, src = _rows()
    suspect = []
    for q in qs:
        text = src.get(q["prov_unit_id"], "")
        for t, correct in ch.get(q["id"], []):
            if not correct:
                continue
            aw = prose._content_words(t, "nl")
            for n in _numbers(t):
                if not _stated_near(text, n, aw):
                    suspect.append((q["prov_ref"], n, t[:55]))
    assert not suspect, f"number not stated where the answer claims: {suspect[:8]}"


def test_the_bank_is_still_behind_the_review_gate():
    """Law-seeded questions are authored, not official. Nothing may reach the
    player until a human has approved it — this asserts the gate is shut, so the
    day it opens it is because someone decided to open it."""
    if not _have():
        print("    (skipped: no Dutch bank built)")
        return
    conn = sqlite3.connect(BANK)
    by_status = dict(conn.execute(
        "SELECT review_status, count(*) FROM questions GROUP BY 1").fetchall())
    assert by_status.get("auto_approved", 0) == 0, \
        "no Dutch question may auto-approve: none of them is an official catalogue"
    print(f"    (bank status: {by_status})")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} tests passed")
