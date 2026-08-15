"""Tests for the EU layer — the Union-law registry member, its deterministic
tagger and the EUR-Lex parser.

Two properties carry most of the weight here. First, the layer must stay a
*sourcing* member: it grounds portable content and must never grow into a third
traffic base, which would change the whole scope taxonomy. Second, an EU act
exists in 24 equally authentic languages, so refs and themes have to be
language-neutral — otherwise the same provision is a different unit in Dutch than
in English and nothing lines up across banks.

The tests that need the raw cache skip when it is absent.

Run with `python tests/test_eu.py`.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import countries, jurisdictions, scope                    # noqa: E402
from src.countries import eu, eu_themes                            # noqa: E402
from src.parsers import eurlex                                     # noqa: E402

RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "data", "raw")


def _manifest(source_id: str, lang: str):
    p = os.path.join(RAW, source_id, lang, "manifest.json")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def test_eu_is_registered_as_a_sourcing_only_layer():
    c = countries.get("EU")
    assert c is eu.COUNTRY
    assert not c.permits, "the EU layer carries no exam and no player bundle"
    for s in c.sources:
        assert s.kind == "eurlex", f"{s.id}: unexpected kind {s.kind!r}"
        assert s.celex and s.celex[0] in "03", f"{s.id} needs a CELEX number"
        assert s.default_theme in c.themes


def test_the_eu_layer_adds_no_regime_node_and_no_new_base():
    """A design category is not a third traffic code. If the EU layer ever
    produced a jurisdiction node or a fourth base, every scope decision and the
    player's National/Common-core toggle would shift under it."""
    assert scope.BASES == ("universal", "cevni", "colregs")
    for code in jurisdictions.codes():
        j = jurisdictions.get(code)
        assert j.derives_from != "EU", f"{code} must not derive from the EU layer"
    assert "EU-INLAND" not in jurisdictions.REGISTRY
    assert "EU-MARITIME" not in jurisdictions.REGISTRY


def test_the_reuse_basis_is_recorded_and_standards_are_excluded():
    """EUR-Lex reuse rests on Commission Decision 2011/833/EU. The EN ISO
    standards the directives point at are NOT covered by it — they are sold per
    copy — so the boundary has to be written down, not assumed."""
    assert "2011/833/EU" in eu.LEGAL_BASIS
    for s in eu.SOURCES:
        assert "2011/833/EU" in s.licence, f"{s.id}: licence must name the decision"
        assert "eur-lex.europa.eu" in s.licence.lower()
    standards = [r for r in eu.REFERENCES if "EN ISO" in r.name]
    assert standards, "the harmonised standards must be documented as excluded"
    assert "NOT ingested" in standards[0].note


# --- the deterministic tagger --------------------------------------------------

def test_articles_and_annexes_map_by_number_not_by_keyword():
    """The mapping is read off each act's own article titles: the Recreational
    Craft Directive puts exhaust emissions in art. 21 and noise in art. 22, and
    its design categories in Annex I — in no article at all."""
    cases = {
        "Directive 2013/53/EU art. 2": "scope_definitions",
        "Directive 2013/53/EU art. 4": "craft_design",
        "Directive 2013/53/EU art. 21": "emissions",
        "Directive 2013/53/EU art. 22": "emissions",
        "Directive 2013/53/EU art. 55": "final_provisions",
        "Directive 2013/53/EU Annex I": "craft_design",
        "Directive 2013/53/EU Annex V": "ce_marking",
        "Directive (EU) 2016/1629 art. 6": "vessel_certification",
        "Directive (EU) 2017/2397 art. 10": "qualifications",
        "Directive (EU) 2017/2397 art. 35": "final_provisions",
    }
    for ref, want in cases.items():
        got = eu_themes.tag_theme(ref=ref)
        assert got == want, f"{ref}: {got} != {want}"


def test_a_parenthesised_act_number_is_recognised():
    """Regression: an anchored \\b before "(EU)" never matches — the preceding
    character is a space and "(" is not a word character — so every post-2015 act
    silently fell through to the default theme."""
    assert eu_themes._act_of("Directive (EU) 2016/1629 art. 6") == "(EU) 2016/1629"
    assert eu_themes._act_of("Directive 2013/53/EU art. 6") == "2013/53/EU"


def test_theme_ids_do_not_collide_with_the_colreg_layer():
    """Theme ids are one global namespace (src/scope.py routes on the theme
    alone), so two supra-national layers sharing an id would cross-route."""
    from src.countries import intl_themes
    assert not (set(eu_themes.THEMES) & set(intl_themes.THEMES))


# --- the EUR-Lex parser (needs the raw cache) ---------------------------------

def test_the_same_act_yields_the_same_refs_in_every_language():
    """EUR-Lex localises the word "Article", so a ref built from the page label
    would differ per language and the 24 expressions would never line up. The
    parser emits "art. 12" in all of them."""
    langs = [l for l in ("en", "nl", "de", "fr") if _manifest("rcd", l)]
    if len(langs) < 2:
        print("    (skipped: need >=2 cached languages of data/raw/rcd/)")
        return
    per_lang = {l: eurlex.parse(eu.SOURCES[0], _manifest("rcd", l)) for l in langs}
    base = [u.ref for u in per_lang[langs[0]]]
    for l in langs[1:]:
        assert [u.ref for u in per_lang[l]] == base, f"{l} refs diverge from {langs[0]}"
        assert ([u.theme for u in per_lang[l]]
                == [u.theme for u in per_lang[langs[0]]]), f"{l} themes diverge"
    # ... and the text really is localised, so this is not comparing a cache to
    # itself.
    if "nl" in per_lang and "en" in per_lang:
        assert per_lang["nl"][0].text != per_lang["en"][0].text


def test_recitals_are_never_ingested_as_rules():
    """A directive's recitals ("Whereas …") outnumber its articles and read like
    provisions. Ingesting them would put the legislator's reasoning in the KB as
    if it bound anyone."""
    m = _manifest("rcd", "en")
    if not m:
        print("    (skipped: data/raw/rcd/en/ not fetched)")
        return
    units = eurlex.parse(eu.SOURCES[0], m)
    assert units
    for u in units:
        assert " art. " in u.ref or " Annex" in u.ref, f"unexpected ref {u.ref!r}"
    # the RCD has 58 articles and 9 annexes; recitals (53 of them) are excluded
    arts = [u for u in units if " art. " in u.ref]
    assert len(arts) == 58, f"expected 58 articles, got {len(arts)}"


def test_the_design_category_table_survives_flattening():
    """Annex I's grid IS the rule: category A/B/C/D against wind force and
    significant wave height. Collecting only loose paragraphs drops the table and
    leaves an annex that looks complete but has lost its numbers."""
    m = _manifest("rcd", "en")
    if not m:
        print("    (skipped: data/raw/rcd/en/ not fetched)")
        return
    annex1 = [u for u in eurlex.parse(eu.SOURCES[0], m)
              if u.ref.endswith("Annex I")]
    assert annex1, "Annex I must be ingested"
    text = annex1[0].text
    for token in ("Wind force", "Significant wave height", "exceeding 8",
                  "up to, and including, 4"):
        assert token in text, f"missing {token!r} — the category table was dropped"


def test_an_unstructured_rendition_is_never_passed_off_as_the_act():
    """EUR-Lex serves the consolidated text without the ELI article skeleton in
    some languages (NL and FR for the RCD). That parses to *zero articles* rather
    than to an error, so the fetcher falls back to the OJ text and records which
    one it took."""
    for lang in ("en", "nl", "de", "fr"):
        m = _manifest("rcd", lang)
        if not m:
            continue
        assert m.get("text_status") in ("consolidated", "as-published"), lang
        assert m.get("legal_version"), lang
        units = eurlex.parse(eu.SOURCES[0], m)
        assert len([u for u in units if " art. " in u.ref]) == 58, \
            f"{lang}: articles missing — an unstructured rendition slipped through"


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} tests passed")
