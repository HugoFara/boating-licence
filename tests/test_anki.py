"""Tests for the Anki export/import round-trip (`tools/anki.py`).

No question bank on disk is needed — these build a tiny in-memory bank of
Question objects and exercise the mapping directly:

  * the .apkg is a valid Anki package (zip → SQLite with col/notes/cards) and
    is byte-identical across rebuilds (deterministic ids + pinned zip mtimes);
  * the TSV round-trips: re-reading an unedited export reports every row
    `unchanged`, a text edit reports `edited` and stays structure-locked (the
    correct-answer flags can't move), and a fresh row becomes a `new` pending
    question.

Run with `python tests/test_anki.py`.
"""

import json
import os
import sqlite3
import sys
import tempfile
import zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import anki                                  # noqa: E402
from src.questions.schema import Question, Choice, Provenance  # noqa: E402


def _bank():
    prov = Provenance(unit_id="oni-art16", ref="ONI art. 16", source="ONI (RS 747.201.1)",
                      url="https://example.test/oni", as_of="2022-01-01", licence="public-domain")
    q1 = Question(
        id="q-oni-art16-aaaa1111", theme="signalisation", kind="rule_mc",
        stem="Que signifie un feu rouge fixe ?", lang="fr",
        choices=[Choice("Passage interdit", is_correct=True),
                 Choice("Passage autorisé"), Choice("Ralentir")],
        explanation="Rouge fixe = interdiction.", review_status="approved",
        generator="seed:test", provenance=prov)
    q2 = Question(
        id="q-meteo-bise-bbbb2222", theme="meteorologie", kind="meteo_mc",
        stem="La bise vient de quelle direction ?", lang="fr",
        choices=[Choice("Nord-est", is_correct=True), Choice("Sud-ouest"),
                 Choice("Ouest", is_correct=True)],
        explanation="", review_status="auto_approved", generator="seed:test",
        provenance=Provenance(unit_id="meteo_vents-bise", ref="MétéoSuisse",
                              source="MétéoSuisse", url="", as_of="", licence="CC BY-SA"))
    return [q1, q2]


def test_apkg_is_valid_and_deterministic():
    qs = _bank()
    with tempfile.TemporaryDirectory() as d:
        p1 = os.path.join(d, "a.apkg")
        p2 = os.path.join(d, "b.apkg")
        anki._build_apkg(qs, "fr", p1)
        anki._build_apkg(qs, "fr", p2)
        assert open(p1, "rb").read() == open(p2, "rb").read(), "apkg not byte-stable"
        with zipfile.ZipFile(p1) as z:
            names = set(z.namelist())
            assert "collection.anki2" in names and "media" in names
            assert json.loads(z.read("media")) == {}   # these two questions have no image
            with tempfile.NamedTemporaryFile(suffix=".anki2", delete=False) as tf:
                tf.write(z.read("collection.anki2"))
                col = tf.name
    try:
        conn = sqlite3.connect(col)
        assert conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0] == 2
        assert conn.execute("SELECT COUNT(*) FROM cards").fetchone()[0] == 2
        decks = json.loads(conn.execute("SELECT decks FROM col").fetchone()[0])
        # default deck + one subdeck per theme used (signalisation, meteorologie)
        assert len([n for n in decks.values() if "::" in n["name"]]) == 2
        # the front field never leaks the answer (no correct marker in Choices)
        flds = conn.execute("SELECT flds FROM notes WHERE guid=?",
                            ("q-oni-art16-aaaa1111",)).fetchone()[0].split("\x1f")
        assert "Réponse" not in flds[3] and "Réponse" in flds[4]
        conn.close()
    finally:
        os.remove(col)


def test_tsv_roundtrip_unchanged():
    qs = _bank()
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "x.tsv")
        anki._write_tsv(qs, p)
        rows = anki._read_tsv(p)
        assert len(rows) == 2
        by_id = {q.id: q for q in qs}
        for row in rows:
            q, status = anki._to_question(row, by_id[row["id"]])
            assert status == "unchanged" and q is None
        # the multi-correct question kept both correct indices through the TSV
        r2 = next(r for r in rows if r["id"] == "q-meteo-bise-bbbb2222")
        assert r2["correct"] == [0, 2]


def test_tsv_edit_is_structure_locked():
    qs = _bank()
    q1 = qs[0]
    row = anki._read_tsv  # silence linters
    # forge an edited row: change the stem AND reorder/retext choices; the correct
    # flag must stay on the ORIGINAL index 0, never follow the edited text.
    edited = {"id": q1.id, "lang": "fr", "theme": "signalisation", "kind": "rule_mc",
              "polarity": "affirmative", "stem": "Feu rouge fixe : que faire ?",
              "choices": ["Ne pas passer", "On peut passer", "Ralentir"],
              "correct": [1],            # <-- import claims index 1; must be ignored
              "explanation": "Edited.", "source_ref": "", "source_url": "",
              "source_as_of": "", "image": None}
    q, status = anki._to_question(edited, q1)
    assert status == "edited" and q is not None
    assert q.review_status == "pending"          # re-enters the review gate
    assert q.correct == [0]                       # structure-locked to the original
    assert q.choices[0].text == "Ne pas passer"   # but the text was updated
    assert q.stem == "Feu rouge fixe : que faire ?"


def test_tsv_new_row_becomes_pending():
    new = {"id": "", "lang": "fr", "theme": "matelotage", "kind": "matelotage_mc",
           "polarity": "affirmative", "stem": "Quel nœud pour amarrer ?",
           "choices": ["Nœud de chaise", "Nœud plat", "Nœud de cabestan"],
           "correct": [0], "explanation": "", "source_ref": "Test", "source_url": "",
           "source_as_of": "", "image": None}
    q, status = anki._to_question(new, None)
    assert status == "new" and q is not None
    assert q.review_status == "pending"
    assert q.correct == [0]
    assert q.provenance.unit_id.startswith("anki-import:")
    # a new row with no correct column is rejected, not silently published
    bad = dict(new, correct=[])
    q2, status2 = anki._to_question(bad, None)
    assert q2 is None and status2.startswith("invalid")


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"\n{len(tests)} tests passed")
