"""The catalogue-coverage doc block stays in sync with the committed lock.

Each country doc carries a `coverage:auto` block generated from the committed
`data/coverage.lock.json` — the SAME source the static player reads — so the docs
and the player can never quote different numbers. This pins that the committed
docs match `run.py coverage-docs` for the committed lock (deterministic + offline;
no built banks required, mirroring tests/test_path.py's path-doc sync check).

Run with `python tests/test_coverage_docs.py`.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import run                                                       # noqa: E402

_DOCS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs")


def test_coverage_docs_in_sync():
    for code in ("CH", "DE", "FR"):
        path = os.path.join(_DOCS, run._PATH_DOC_FILE[code])
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        assert run._COV_DOC_START in text and run._COV_DOC_END in text, code
        block = text[text.index(run._COV_DOC_START):text.index(run._COV_DOC_END)]
        assert run._coverage_doc_section(code) in block, (
            f"docs/{run._PATH_DOC_FILE[code]} out of sync — "
            f"run `python run.py coverage-docs`")


def test_official_bank_gets_a_note_not_a_score():
    # DE IS the catalogue: its block states so and never prints a coverage %.
    sec = run._coverage_doc_section("DE")
    assert "ELWIS" in sec and "%" not in sec


def test_derived_banks_carry_the_floor_caveat():
    # CH/FR must carry the honest "not exam-ready" framing, never an implied pass.
    # The caveat holds an {ambiguous} placeholder filled from the lock at render time,
    # so check stable, placeholder-free fragments rather than the raw template.
    fragments = {"fr": ["plancher", "inconnu", "couverture démontrée"],
                 "de": ["Untergrenze", "unbekannt", "nachgewiesene Abdeckung"]}
    for code in ("CH", "FR"):
        sec = run._coverage_doc_section(code).lower()
        for frag in fragments[run._PATH_DOC_LANG[code]]:
            assert frag.lower() in sec, (code, frag)
        # the ambiguity figure must be substituted, not left as a literal placeholder
        assert "{ambiguous}" not in sec


def test_whole_bank_composite_is_surfaced():
    # The reviewer's "third number": demonstrated + unknown of the WHOLE bank must
    # both reach the doc, not just the flattering measured-slice figure.
    for code in ("CH", "FR"):
        lang = run._PATH_DOC_LANG[code]
        sec = run._coverage_doc_section(code)
        cols = run._COV_DOC_CHROME[lang]["cols"]
        # the demonstrated + unknown columns are present as headers...
        assert cols[1] in sec and cols[2] in sec
        # ...and at least one demonstrated value is bolded (the headline number).
        assert "**" in sec


if __name__ == "__main__":
    for _name, _fn in sorted(globals().items()):
        if _name.startswith("test_") and callable(_fn):
            _fn()
            print("ok", _name)
