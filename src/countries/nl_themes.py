"""Dutch exam-theme taxonomy + tagger (Klein Vaarbewijs I / II).

Two official documents define this taxonomy between them, and nothing here is
invented:

* **What the exam covers** — *Binnenvaartregeling* art. 7.15 lists the subjects
  of the klein-vaarbewijs exam by law. Lid 1 (KVB I): the legal provisions
  relevant to safe navigation on rivers, canals and lakes; handling the
  propulsion machinery; safety measures; the waterways, the state of the fairway
  and elementary meteorology; and navigating, manoeuvring and what to do in
  special circumstances. Lid 2 (KVB II) adds: the legal provisions for the
  Westerschelde, the Eems and the Dollard; the use of nautical publications;
  course and position fixing; and meteorology.
* **How the legal provisions are organised** — the *Binnenvaartpolitiereglement*
  (BPR) splits them into chapters, and chapter 3 (optische tekens), 4
  (geluidsseinen), 5 (verkeerstekens) and 6 (vaarregels) are exactly the four
  blocks a learner studies. So the "wettelijke bepalingen" subject is realised
  here as one theme per BPR chapter rather than as a single opaque bucket.

That split is what makes the tagger **deterministic** for the ingested law: a
Dutch article number is always chapter-qualified ("Artikel 5.01" is in chapter 5,
with no exception anywhere in the BPR), so the chapter — hence the theme — is
read straight off the ref. Annexes map by their own number. Keyword rules are the
fallback for the acts outside the BPR (the Binnenvaartwet/-besluit/-regeling
licensing spine) and for anything reaching the tagger without a parseable ref.

Labels are Dutch: the exam is Dutch, its sources are Dutch-only (Dutch law is
enacted in one language), and the German bank sets the precedent that a national
bank speaks its own language.
"""

from __future__ import annotations

import re

# Canonical theme ids (stable keys) -> human label (Dutch, as on the exam).
THEMES: dict[str, str] = {
    # --- "wettelijke bepalingen", realised as the BPR's own chapter split -----
    "algemene_bepalingen": "Algemene bepalingen en kentekens",
    "optische_tekens": "Optische tekens van schepen (lichten en dagmerken)",
    "geluidsseinen": "Geluidsseinen",
    "marifoon_radar": "Marifoon, radar en Inland AIS",
    "verkeerstekens": "Verkeerstekens",
    "betonning": "Markering van het vaarwater (betonning)",
    "vaarregels": "Vaarregels",
    "ligplaats": "Ligplaats nemen",
    "bijzondere_vaarwegen": "Bijzondere bepalingen per vaarweg",
    "vaarbewijs": "Vaarbewijs, registratie en handhaving",
    # --- the non-BPR exam subjects (art. 7.15) --------------------------------
    "voortstuwing": "Behandeling van de voortstuwingswerktuigen",
    "veiligheid": "Veiligheidsmaatregelen",
    "vaarwater": "Waterwegen en omstandigheden van het vaarwater",
    "manoeuvreren": "Varen, manoeuvreren en bijzondere omstandigheden",
    "milieu": "Milieu en afvalstoffen",
    # --- KVB II only ----------------------------------------------------------
    "navigatie": "Nautische bescheiden, koers- en plaatsbepaling",
    # id deliberately not "meteorologie": that key is already the Swiss theme,
    # and theme ids are a single global namespace (see tests/test_countries.py).
    "weerkunde": "Meteorologie",
}

# Themes no ingested *law* source grounds — they are seamanship and craft
# subjects the statute names (art. 7.15) but no ordinance spells out. Scaffolded
# so a law-only Dutch build stays clean (see normalize's missing-theme check).
EXTENSION_THEMES: frozenset[str] = frozenset(
    {"voortstuwing", "vaarwater", "manoeuvreren", "navigatie", "weerkunde"})

# Which themes each permit's exam draws on (Binnenvaartregeling art. 7.15).
_KVB1 = ("algemene_bepalingen", "optische_tekens", "geluidsseinen",
         "marifoon_radar", "verkeerstekens", "betonning", "vaarregels",
         "ligplaats", "bijzondere_vaarwegen", "vaarbewijs", "voortstuwing",
         "veiligheid", "vaarwater", "manoeuvreren", "milieu")
# Lid 2 is explicitly cumulative — "de in het eerste lid genoemde onderwerpen
# alsmede …" — so KVB II is KVB I plus navigation and meteorology.
_KVB2 = _KVB1 + ("navigatie", "weerkunde")

PERMIT_THEMES: dict[str, tuple[str, ...]] = {
    "KVB-1": _KVB1,
    "KVB-2": _KVB2,
}

# --- deterministic mapping for the ingested law -------------------------------
# BPR chapter -> theme. Chapters 8-13 are the per-waterway special provisions.
_CHAPTER_THEME: dict[str, str] = {
    "1": "algemene_bepalingen", "2": "algemene_bepalingen",
    "3": "optische_tekens",
    "4": "geluidsseinen", "4A": "marifoon_radar",
    "5": "verkeerstekens",
    "6": "vaarregels",
    "7": "ligplaats",
    "8": "bijzondere_vaarwegen", "9": "bijzondere_vaarwegen",
    "10": "bijzondere_vaarwegen", "11": "bijzondere_vaarwegen",
    "12": "bijzondere_vaarwegen", "13": "bijzondere_vaarwegen",
}

# Annexes that carry the SAME subject in both police reglementen — checked
# against each act's own annex titles, not assumed: 1 (home-port letters), 3
# (optische tekens), 6 (geluidsseinen), 7 (verkeerstekens), 8 (markering van het
# vaarwater = the IALA-A buoyage annex) and 13 (scheepsbescheiden).
_ANNEX_THEME: dict[str, str] = {
    "1": "algemene_bepalingen", "3": "optische_tekens", "6": "geluidsseinen",
    "7": "verkeerstekens", "8": "betonning", "13": "algemene_bepalingen",
}

# The rest of the numbering diverges between the two — BPR bijlage 11 is a list of
# waterways, RPR bijlage 11 is the Inland AIS data set — so these apply only to
# the BPR. Bijlage 10, 11 and 14-18 list the waterways a chapter-9/10 rule covers.
_ANNEX_THEME_BPR: dict[str, str] = {
    "4": "marifoon_radar", "9": "marifoon_radar", "12": "veiligheid",
    "10": "bijzondere_vaarwegen", "11": "bijzondere_vaarwegen",
    "14": "bijzondere_vaarwegen", "15": "bijzondere_vaarwegen",
    "16": "bijzondere_vaarwegen", "17": "bijzondere_vaarwegen",
    "18": "bijzondere_vaarwegen",
}

# The chapter/annex mapping is a fact about the two police reglementen (their
# chapters 1-7 are subject-for-subject identical), NOT about Dutch law at large:
# "Artikel 7.15" of the Binnenvaartregeling is an exam rule, not a berthing rule.
_POLITIEREGLEMENT = re.compile(r"politiereglement", re.I)
_BPR = re.compile(r"binnenvaartpolitiereglement", re.I)

_ARTICLE_REF = re.compile(r"\bartikel\s+(\d+[A-Z]?)\.\d", re.I)
_ANNEX_REF = re.compile(r"\bbijlage\s+(\d+)", re.I)

# Keyword fallback, ordered most-specific first. Used for the licensing acts
# (Binnenvaartwet/-besluit/-regeling) and any unit without a parseable ref.
_KEYWORDS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("vaarbewijs", re.compile(
        r"\b(vaarbewijs|vaarbewijzen|kwalificatiecertificaat|dienstboekje|"
        r"examen|geneeskundige verklaring|gezondheidsverklaring|"
        r"ongeldigverklaring|vaarbevoegdheid|register)\b", re.I)),
    ("marifoon_radar", re.compile(r"\b(marifoon|marifonie|radar|AIS)\b", re.I)),
    ("geluidsseinen", re.compile(
        r"\b(geluidssein\w*|geluidsein\w*|scheepsklok|stoot|lange stoot|"
        r"korte stoot|mistsein\w*)\b", re.I)),
    ("optische_tekens", re.compile(
        r"\b(licht(en|voering)?|toplicht|boordlicht\w*|heklicht|rondom schijnend|"
        r"dagmerk\w*|bol|kegel|cilinder|ruit)\b", re.I)),
    ("betonning", re.compile(
        r"\b(betonning|markering van het vaarwater|boei\w*|ton(nen)?|"
        r"spitse ton|stompe ton|kardinale)\b", re.I)),
    ("verkeerstekens", re.compile(
        r"\b(verkeersteken\w*|verbodsteken\w*|gebodsteken\w*|"
        r"beperkingsteken\w*|aanwijzingsteken\w*|bord)\b", re.I)),
    ("vaarregels", re.compile(
        r"\b(voorrang|uitwijk\w*|koers\w* houden|oplopen|voorbijlopen|"
        r"tegengestelde koersen|stuurboord|bakboord|vaarregel\w*)\b", re.I)),
    ("ligplaats", re.compile(r"\b(ligplaats|ankeren|meren|afmeren)\b", re.I)),
    ("milieu", re.compile(
        r"\b(afvalstof\w*|olie|verontreinig\w*|milieu|bilgewater)\b", re.I)),
    ("veiligheid", re.compile(
        r"\b(gevaarlijke stoffen|reddingsmiddel\w*|reddingsvest|brandblus\w*|"
        r"veiligheid\w*)\b", re.I)),
)


def tag_theme(ref: str = "", title: str = "", text: str = "",
              default: str | None = None) -> str:
    """Return the Dutch theme id for a knowledge unit.

    Deterministic for the BPR (chapter from the article number, or the annex
    number); keyword-scanned otherwise; ``default`` last.
    """
    haystack_ref = f"{ref} {title}"
    if _POLITIEREGLEMENT.search(ref or ""):
        m = _ANNEX_REF.search(haystack_ref)
        if m:
            annexes = dict(_ANNEX_THEME)
            if _BPR.search(ref or ""):
                annexes.update(_ANNEX_THEME_BPR)
            if m.group(1) in annexes:
                return annexes[m.group(1)]
        m = _ARTICLE_REF.search(haystack_ref)
        if m and m.group(1).upper() in _CHAPTER_THEME:
            return _CHAPTER_THEME[m.group(1).upper()]

    haystack = " ".join((ref, title, text))
    for theme_id, pattern in _KEYWORDS:
        if pattern.search(haystack):
            return theme_id
    if default and default in THEMES:
        return default
    return "algemene_bepalingen"


def is_valid(theme_id: str) -> bool:
    return theme_id in THEMES
