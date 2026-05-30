"""Tests for the CEVNI-core classifier (`src/cevni.py`).

CEVNI is the harmonised European inland-navigation code; its signs and rules are
portable across signatory states, while national statute and water-body specifics
are not. These checks pin that taxonomy: harmonised content is `cevni`, country
statute / frontier waters are `national`, and named-local weather is `local` — so
the cross-country core bundle stays clean.

Run with `python tests/test_cevni.py`.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import cevni                                    # noqa: E402
from src.questions.schema import Question, Choice, Provenance  # noqa: E402


def _q(theme, stem="", ref="", source=""):
    """A minimal Question for classification (classify reads theme + ref/source/
    stem only; the choices/ids are placeholders)."""
    return Question(id="t", theme=theme, kind="rule_mc", stem=stem,
                    choices=[Choice("a", is_correct=True), Choice("b")],
                    provenance=Provenance(unit_id="u", ref=ref, source=source, url=""))


def test_scopes_vocabulary():
    assert cevni.SCOPES == {"cevni", "national", "local"}
    assert cevni.DEFAULT_SCOPE in cevni.SCOPES


def test_classify_always_returns_a_valid_scope():
    for theme in ("signalisation", "lois", "meteorologie", "matelotage",
                  "definitions", "voile", "eaux_frontalieres"):
        assert cevni.classify(_q(theme, "texte quelconque")) in cevni.SCOPES


def test_harmonised_signage_is_cevni():
    assert cevni.classify(_q("signalisation", "Que signifie ce panneau ?")) == "cevni"


def test_frontier_waters_are_national():
    # by theme…
    assert cevni.classify(_q("eaux_frontalieres", "règle sur le lac")) == "national"
    # …and by wording, even under another theme
    assert cevni.classify(_q("lois", "selon la convention franco-suisse")) == "national"


def test_meteo_local_vs_portable():
    assert cevni.classify(_q("meteorologie", "la bise s'établit sur le Léman")) == "local"
    assert cevni.classify(_q("meteorologie", "formation des nuages et des fronts")) == "cevni"


def test_national_statute_within_lois():
    assert cevni.classify(_q("lois", "couverture d'assurance-responsabilité civile exigée")) == "national"
    # a genuine CEVNI navigation rule stays cevni
    assert cevni.classify(_q("lois", "croisement et dépassement des bateaux")) == "cevni"


def test_universal_themes_are_cevni():
    for theme in ("matelotage", "definitions", "voile"):
        assert cevni.classify(_q(theme, "contenu portable")) == "cevni"


def test_bodensee_signage_is_guarded_out_of_the_core():
    # A harmonised-looking signalisation question, but tied to the non-CEVNI
    # Bodensee regime (BSO) — must NOT be classified cevni.
    q = _q("signalisation", "Que signifie ce signal ?",
           ref="BSO Annexe", source="Bodensee-Schifffahrts-Ordnung")
    assert cevni.classify(q) == "local"
    assert q not in cevni.core_bank([q])


def test_core_bank_is_a_clean_subset():
    qs = [
        _q("signalisation", "panneau"),               # cevni
        _q("matelotage", "nœud de chaise"),           # cevni
        _q("eaux_frontalieres", "frontière"),         # national
        _q("meteorologie", "la vaudaire"),            # local
    ]
    core = cevni.core_bank(qs)
    assert all(cevni.classify(q) == "cevni" for q in core)
    assert len(core) == 2                              # the two cevni ones
    assert all(q in qs for q in core)                  # a strict subset, nothing invented


def test_scope_counts_partition_the_input():
    qs = [_q("signalisation"), _q("eaux_frontalieres"), _q("meteorologie", "joran")]
    counts = cevni.scope_counts(qs)
    assert set(counts) == cevni.SCOPES
    assert sum(counts.values()) == len(qs)
    assert counts["cevni"] == 1 and counts["national"] == 1 and counts["local"] == 1


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"\n{len(tests)} tests passed")
