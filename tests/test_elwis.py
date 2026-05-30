"""Tests for the ELWIS catalogue ingester (`src/questions/elwis.py`).

Offline: a tiny gii-shaped HTML fixture (the Anmerkung header + three questions,
one carrying a sign figure) is parsed and the resulting `Question`s are checked —
questions are verbatim, the published first option (`a`) stays the correct one
after the deterministic shuffle, the figure question gets its asset path, the
German tagger classifies each, and every question carries the §5 attribution as
an auto-approved `official_mc`. A second check pins the shared-Basisfragen dedup.
No network.

Run with `python tests/test_elwis.py`.
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.questions import elwis                          # noqa: E402
from src.questions.schema import Question, Choice, Provenance, validate  # noqa: E402
from src.countries import de_themes                      # noqa: E402

# One section page in the real ELWIS shape: numbered <p> stems, each followed by
# an <ol class="elwisOL-lowerLiteral"> of four <li> options (option a first =
# correct), with a sign figure as a sibling <p class="picture"><img>.
_FIXTURE = """<!doctype html><html><body>
<div id="content">
<h1>Spezifische Fragen Binnen</h1>
<p class="wsv-red"><strong>Anmerkung:<br/>Antwort a ist immer die richtige.</strong></p>
<p>1. Wie weichen zwei Motorboote aus, die sich auf entgegengesetzten Kursen nähern?</p>
<ol class="elwisOL-lowerLiteral" start="1" type="a">
<li>Jedes Fahrzeug muss seinen Kurs nach Steuerbord ändern.<br/><br/></li>
<li>Jedes Fahrzeug muss seinen Kurs nach Backbord ändern.<br/><br/></li>
<li>Das luvwärtige Fahrzeug muss ausweichen.<br/><br/></li>
<li>Das leewärtige Fahrzeug muss ausweichen.<br/><br/></li>
</ol>
<p class="line"></p>
<p>2. Was bedeutet dieses Tafelzeichen?<br/>
<p class="picture linksOhne normal" style="width:60px;">
<span class="wrapper"><img src="https://www.elwis.de/DE/Schifffahrtsrecht/Binnenschifffahrtsrecht/Grafiken/Anlage-07/Hinweiszeichen-E057.gif?__blob=normal&amp;v=1" alt="Hinweiszeichen E.5.7"/></span></p>
</p>
<ol class="elwisOL-lowerLiteral" start="1" type="a">
<li>Liegestelle für alle Fahrzeuge.<br/><br/></li>
<li>Liegestelle für Fahrzeuge mit explosiven Stoffen.<br/><br/></li>
<li>Liegestelle für Fahrzeuge mit brennbaren Stoffen.<br/><br/></li>
<li>Liegestelle für Fahrzeuge mit gesundheitsgefährdeten Stoffen.<br/><br/></li>
</ol>
<p class="line"></p>
<p>3. Was kündigt eine Sturmwarnung an?</p>
<ol class="elwisOL-lowerLiteral" start="1" type="a">
<li>Auffrischenden Wind und zunehmenden Seegang.<br/><br/></li>
<li>Nachlassenden Wind.<br/><br/></li>
<li>Gleichbleibendes Wetter.<br/><br/></li>
<li>Dichten Nebel.<br/><br/></li>
</ol>
</div></body></html>
"""

_CAT = elwis.CATALOGUES["binnen"]


def _parse_fixture():
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False,
                                     encoding="utf-8") as fh:
        fh.write(_FIXTURE)
        path = fh.name
    # elwis.parse joins each section path under repo-root; an absolute path makes
    # os.path.join return it unchanged, so the fixture resolves directly.
    manifest = {
        "images": {"Hinweiszeichen-E057.gif":
                   {"path": "data/assets/elwis/binnen/de/Hinweiszeichen-E057.gif",
                    "url": "https://example.invalid/x.gif"}},
        "sections": [{"block": "spezifisch_binnen",
                      "url": "https://www.elwis.de/x", "path": path}],
    }
    try:
        return elwis.parse(_CAT, manifest)
    finally:
        os.unlink(path)


def test_three_questions_parsed_verbatim():
    qs = _parse_fixture()
    assert len(qs) == 3, "three numbered questions expected"
    by_ref = {q.provenance.ref: q for q in qs}
    assert set(by_ref) == {"Frage 1", "Frage 2", "Frage 3"}
    # verbatim stem + verbatim option text (no rewording/translation)
    assert by_ref["Frage 1"].stem == \
        "Wie weichen zwei Motorboote aus, die sich auf entgegengesetzten Kursen nähern?"
    texts = {c.text for c in by_ref["Frage 3"].choices}
    assert "Auffrischenden Wind und zunehmenden Seegang." in texts


def test_first_option_is_correct_after_shuffle():
    # The published option `a` is the answer; it must remain the correct choice
    # even though display order is permuted (so "a is always first" is no tell).
    for q in _parse_fixture():
        assert len(q.choices) == 4
        assert sum(c.is_correct for c in q.choices) == 1
        correct = [c for c in q.choices if c.is_correct][0]
        # the correct text is the published first option of that question
        assert correct.text.endswith(".")
    q1 = [q for q in _parse_fixture() if q.provenance.ref == "Frage 1"][0]
    assert [c for c in q1.choices if c.is_correct][0].text == \
        "Jedes Fahrzeug muss seinen Kurs nach Steuerbord ändern."
    # not every question keeps the answer in position 0 (shuffle actually moved some)
    positions = [q.correct[0] for q in _parse_fixture()]
    assert any(p != 0 for p in positions), "deterministic shuffle should move answers"


def test_figure_question_links_its_asset():
    q2 = [q for q in _parse_fixture() if q.provenance.ref == "Frage 2"][0]
    assert q2.image == "data/assets/elwis/binnen/de/Hinweiszeichen-E057.gif"
    assert q2.theme == "schifffahrtszeichen"        # "Tafelzeichen" keyword


def test_themes_and_blocks_assigned():
    by_ref = {q.provenance.ref: q for q in _parse_fixture()}
    assert by_ref["Frage 1"].theme == "verkehrsregeln"     # ausweichen/Kurs
    assert by_ref["Frage 3"].theme == "wetterkunde"        # Sturmwarnung/Seegang
    assert all(q.block == "spezifisch_binnen" for q in by_ref.values())


def test_provenance_licence_and_status():
    q = _parse_fixture()[0]
    assert q.kind == "official_mc" and q.lang == "de"
    assert q.review_status == "auto_approved"
    assert "elwis.de" in q.provenance.licence and "§5(2)" in q.provenance.licence
    assert q.provenance.source.startswith("ELWIS Fragenkatalog SBF Binnen")
    assert validate(q, is_valid_theme=de_themes.is_valid) == []   # valid German q


def test_shared_basisfragen_deduped():
    def basis(stem, n, cat):
        return Question(
            id=f"{cat}-{n}", theme="verkehrsregeln", kind="official_mc",
            stem=stem, lang="de", block="basis", choices=[Choice("a", is_correct=True),
            Choice("b")], provenance=Provenance(unit_id=f"{cat}-{n}", ref="", source="",
            url=""))
    shared = "Was ist zu tun, wenn unklar ist, wer Schiffsführer ist?"
    qs = [basis(shared, 1, "binnen"),
          basis("Ein Binnen-spezifischer Stem.", 2, "binnen"),
          Question(id="b-spez", theme="verkehrsregeln", kind="official_mc",
                   stem="spez", lang="de", block="spezifisch_binnen",
                   choices=[Choice("a", is_correct=True), Choice("b")],
                   provenance=Provenance(unit_id="b-spez", ref="", source="", url="")),
          basis(shared, 1, "see")]                 # same basis question from See
    kept, dropped = elwis.dedup_shared_basis(qs)
    assert dropped == 1 and len(kept) == 3
    # the duplicate dropped is the See basis copy; non-basis is never deduped
    assert [q.id for q in kept] == ["binnen-1", "binnen-2", "b-spez"]


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"\n{len(tests)} tests passed")
