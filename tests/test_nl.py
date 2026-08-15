"""Tests for the Netherlands layer — the country model, the Dutch theme tagger
and the BWB (wetten.overheid.nl) parser.

The contract these pin down is mostly *sourcing discipline*: every legal fact in
`src/countries/nl.py` is supposed to come from a named Dutch act, and the theme
tagger is supposed to be deterministic for the police reglementen rather than
guessing from keywords. The tests that need the raw law cache skip when it is
absent, so the suite runs on a clean checkout.

Run with `python tests/test_nl.py`.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import countries, jurisdictions                          # noqa: E402
from src.countries import nl, nl_themes                            # noqa: E402
from src.parsers import bwb                                        # noqa: E402

RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "data", "raw")


def _have_bpr() -> bool:
    return os.path.exists(os.path.join(RAW, "bpr", "nl", "manifest.json"))


def test_nl_is_registered_with_dutch_law_sources():
    c = countries.get("NL")
    assert c is nl.COUNTRY
    assert c.default_lang == "nl" and c.langs == ("nl",)
    assert c.sources, "the Netherlands must register law sources"
    for s in c.sources:
        assert s.kind == "bwb", f"{s.id}: unexpected kind {s.kind!r}"
        assert s.bwb_id.startswith("BWBR"), f"{s.id} needs a BWB id"
        assert s.default_theme in c.themes
    ids = {s.id for s in c.sources}
    # the traffic codes + the licensing spine that defines the permits
    assert {"bpr", "rpr", "stz"} <= ids
    assert {"binnenvaartwet", "binnenvaartbesluit", "binnenvaartregeling"} <= ids


def test_the_reuse_basis_is_the_dutch_no_copyright_rule():
    """Dutch law is not merely *licensed* for reuse — Auteurswet art. 11 says no
    copyright exists on it at all. The distinction matters, so it must be the one
    recorded."""
    basis = nl.LEGAL_BASIS
    assert "Auteurswet art. 11" in basis
    assert "geen auteursrecht" in basis
    for s in nl.SOURCES:
        assert "Auteurswet" in s.licence, f"{s.id}: licence must name the basis"


def test_both_permits_are_inland_and_kvb2_extends_kvb1():
    p = nl.COUNTRY.permits
    assert set(p) == {"KVB-1", "KVB-2"}
    # The Netherlands requires no recreational licence at sea, so neither permit
    # is maritime — even KVB II's "maritime-nature" waters are binnenwateren.
    for permit in p.values():
        assert jurisdictions.permit_track(permit) == "inland"
    # Binnenvaartregeling art. 7.15 lid 2 is cumulative: KVB II = KVB I + more.
    t1, t2 = set(p["KVB-1"].themes), set(p["KVB-2"].themes)
    assert t1 < t2, "KVB II must strictly extend KVB I's subjects"
    assert t2 - t1 == {"navigatie", "weerkunde"}


def test_exam_scoring_matches_the_cbr_paper():
    """CBR scores by weighted question and passes at 70 %. If pass_points ever
    stops being 70 % of total_points, one of the two was edited without the other."""
    for code in ("KVB-1", "KVB-2"):
        e = nl.COUNTRY.permits[code].exam
        assert e.scoring == "all_or_nothing"
        assert e.total_points and e.pass_points
        assert round(e.pass_points / e.total_points, 2) == 0.70, code
        # weights vary per question, so a flat points_per_question would be a lie
        assert e.points_per_question is None, code


def test_the_maritime_waters_list_is_the_statutory_one():
    """Binnenvaartregeling art. 7.11b lid 2 enumerates the wateren van maritieme
    aard. That list IS the KVB I/KVB II boundary, so it must not drift."""
    assert nl.MARITIEME_WATEREN == (
        "Westerschelde", "Oosterschelde", "Waddenzee", "Eems", "Dollard",
        "IJsselmeer", "IJmeer", "Markermeer (met uitzondering van de Gouwzee)")
    assert "Gouwzee" in nl.COUNTRY.permits["KVB-2"].note


def test_no_practical_exam_step_is_invented():
    """Unlike CH/DE/FR there is no on-water practical exam for the klein
    vaarbewijs. Adding a `practical` step would invent a legal requirement."""
    codes = [s.code for s in nl.PATH]
    assert "practical" not in codes
    assert {"age", "medical", "application"} <= set(codes)
    for step in nl.PATH:
        assert step.body.get("nl"), f"{step.code}: needs a Dutch body"
        assert step.source and step.url and step.as_of


# --- the theme tagger ---------------------------------------------------------

def test_a_bpr_article_is_tagged_by_its_chapter_not_by_keywords():
    """Dutch article numbers are chapter-qualified, so the tagger is deterministic
    for the police reglementen — no keyword guessing on the canonical text."""
    cases = {
        "Binnenvaartpolitiereglement Artikel 3.08": "optische_tekens",
        "Binnenvaartpolitiereglement Artikel 4.01": "geluidsseinen",
        "Binnenvaartpolitiereglement Artikel 5.01": "verkeerstekens",
        "Binnenvaartpolitiereglement Artikel 6.03": "vaarregels",
        "Binnenvaartpolitiereglement Artikel 7.02": "ligplaats",
        "Rijnvaartpolitiereglement 1995 Artikel 6.04": "vaarregels",
    }
    for ref, want in cases.items():
        got = nl_themes.tag_theme(ref=ref, title="", text="")
        assert got == want, f"{ref}: {got} != {want}"


def test_the_chapter_rule_does_not_leak_outside_the_police_reglementen():
    """"Artikel 7.15" of the Binnenvaartregeling is the exam-subject rule, not a
    berthing rule — chapter 7 means 'ligplaats' only inside the BPR/RPR."""
    got = nl_themes.tag_theme(
        ref="Binnenvaartregeling Artikel 7.15", title="",
        text="Het examen ter verkrijging van het klein vaarbewijs I heeft "
             "betrekking op de volgende onderwerpen")
    assert got == "vaarbewijs", got
    assert nl_themes.tag_theme(ref="Binnenvaartpolitiereglement Artikel 7.02",
                               title="", text="") == "ligplaats"


def test_annex_8_is_buoyage_in_both_reglementen():
    """Bijlage 8 is "Markering van het vaarwater" in the BPR and "Verkeerstekens
    ter markering van de vaarweg" in the RPR — the IALA-A buoyage annex either
    way, and the one annex a learner spends most time in."""
    for ref in ("Binnenvaartpolitiereglement Bijlage 8",
                "Rijnvaartpolitiereglement 1995 Bijlage 8"):
        assert nl_themes.tag_theme(ref=ref, title="", text="") == "betonning", ref


def test_bpr_only_annex_numbers_are_not_applied_to_the_rpr():
    """The two acts share annexes 1/3/6/7/8/13 but diverge after that: BPR bijlage
    11 is a list of waterways, RPR bijlage 11 is the Inland AIS data set. Applying
    the BPR map to the RPR would file the AIS annex as a waterway list."""
    assert nl_themes.tag_theme(ref="Binnenvaartpolitiereglement Bijlage 11",
                               title="", text="") == "bijzondere_vaarwegen"
    got = nl_themes.tag_theme(
        ref="Rijnvaartpolitiereglement 1995 Bijlage 11", title="",
        text="Gegevens die in het Inland AIS-apparaat moeten worden ingevoerd")
    assert got == "marifoon_radar", got


def test_extension_themes_are_exactly_the_ungrounded_subjects():
    """The statute names subjects no ordinance spells out (engines, manoeuvring,
    position fixing, weather). They must be declared as extension themes or the
    normalize stage warns about legitimately empty themes on every build."""
    assert nl_themes.EXTENSION_THEMES == frozenset(
        {"voortstuwing", "vaarwater", "manoeuvreren", "navigatie", "weerkunde"})
    for t in nl_themes.EXTENSION_THEMES:
        assert t in nl_themes.THEMES


# --- the BWB parser (needs the raw cache) --------------------------------------

def test_the_amendment_apparatus_never_reaches_the_legal_text():
    """Every BWB provision carries a <meta-data><brondata> block: Staatsblad year,
    number and three dates. Flatten it naively and "2024 104 25-04-2024 …" lands
    at the end of the rule, reading as if it were part of the law."""
    if not _have_bpr():
        print("    (skipped: data/raw/bpr/nl/ not fetched)")
        return
    import re
    with open(os.path.join(RAW, "bpr", "nl", "manifest.json"), encoding="utf-8") as fh:
        manifest = json.load(fh)
    units = bwb.parse(nl.SOURCES[0], manifest)
    assert units, "the BPR must parse to units"
    trailer = re.compile(r"\b(19|20)\d\d \d+ \d\d-\d\d-\d{4}")
    offenders = [u.ref for u in units if trailer.search(u.text)]
    assert not offenders, f"amendment apparatus leaked into: {offenders[:5]}"


def test_every_bpr_article_ref_is_a_citation_a_reader_would_write():
    if not _have_bpr():
        print("    (skipped: data/raw/bpr/nl/ not fetched)")
        return
    with open(os.path.join(RAW, "bpr", "nl", "manifest.json"), encoding="utf-8") as fh:
        manifest = json.load(fh)
    units = bwb.parse(nl.SOURCES[0], manifest)
    for u in units:
        assert u.ref.startswith("Binnenvaartpolitiereglement "), u.ref
        assert u.theme in nl_themes.THEMES, f"{u.ref}: unknown theme {u.theme!r}"
    assert len({u.id for u in units}) == len(units), "unit ids must be unique"


def test_the_official_annex_figures_come_through():
    """The BPR ships its signs, lights, sound patterns and buoyage as official
    PNGs. Losing them silently would be invisible — the text still parses."""
    if not _have_bpr():
        print("    (skipped: data/raw/bpr/nl/ not fetched)")
        return
    with open(os.path.join(RAW, "bpr", "nl", "manifest.json"), encoding="utf-8") as fh:
        manifest = json.load(fh)
    units = bwb.parse(nl.SOURCES[0], manifest)
    figures = sum(len(u.assets) for u in units)
    assert figures > 300, f"expected the BPR's plate set, got {figures} figures"
    with_figs = {u.ref for u in units if u.assets}
    assert any("Bijlage 8" in r for r in with_figs), "no buoyage plates"


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} tests passed")
