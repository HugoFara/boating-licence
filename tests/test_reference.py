"""Tests for the maritime reference corpus (`src/fr/reference_fr.py`).

France's côtière content rests on the IALA Maritime Buoyage System (Region A) and
SHOM tides/charts. These are not openly licensed for verbatim redistribution, so we
ingest the non-copyrightable FACTS — verified against and cited to IALA R1001 /
SHOM — as KnowledgeUnits in the committed `src/fr/reference_kb.json`. These checks
pin that corpus's shape and a couple of load-bearing facts.

Run with `python tests/test_reference.py`.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import themes                       # noqa: E402
from src.fr import themes_fr, reference_fr   # noqa: E402  (themes_fr registers FR themes)

CORPUS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "src", "fr", "reference_kb.json")


def _corpus():
    with open(CORPUS, encoding="utf-8") as fh:
        return json.load(fh)["units"]


def test_reference_corpus_is_well_formed():
    units = _corpus()
    assert len(units) == len(reference_fr.REFERENCE) >= 18
    srcs = {u["source_id"] for u in units}
    assert srcs == {"iala_a", "shom"}
    for u in units:
        assert u["kind"] == "reference"
        assert u["text"].strip() and u["source_url"].startswith("http")
        assert u["licence"].strip()
        assert themes.is_valid(u["theme"]), f"{u['ref']}: bad theme {u['theme']!r}"
        # côtière themes only (this corpus grounds the sea option)
        assert u["theme"] in ("balisage", "meteo_maree")


def test_key_facts_present_and_correct():
    by_ref = {u["ref"]: u["text"] for u in _corpus()}
    # IALA Region A lateral colours (the classic exam trap vs Region B)
    port = next(t for r, t in by_ref.items() if "latérale bâbord" in r)
    star = next(t for r, t in by_ref.items() if "latérale tribord" in r)
    assert "ROUGE" in port and "cylindrique" in port
    assert "VERTE" in star and "conique" in star
    # SHOM coefficient range
    coef = next(t for r, t in by_ref.items() if "coefficient de marée" in r)
    assert "20" in coef and "120" in coef
    # chart datum
    zh = next(t for r, t in by_ref.items() if "zéro hydrographique" in r)
    assert "plus basses mers astronomiques" in zh


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"\n{len(tests)} tests passed")
