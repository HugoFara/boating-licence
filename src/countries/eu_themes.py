"""EU theme taxonomy + tagger for the Union-law layer.

Like the COLREG tagger (:mod:`countries.intl_themes`) this is **deterministic
rather than keyword-driven**, and for a sharper reason: an EU act exists in 24
equally authentic language versions, so a keyword rule would have to be written 24
times and would still tag the same provision differently in Dutch and in German.
Instead the mapping is (act, article number) → theme, and the EUR-Lex parser
emits a language-neutral ref ("Directive 2013/53/EU art. 12") precisely so this
table works unchanged in every language.

Each range below was read off the act's own article titles, never guessed — e.g.
the Recreational Craft Directive puts exhaust emissions in art. 21 and noise
emissions in art. 22, and its design categories A–D are in Annex I, not in any
article at all.

Labels are English: EU law has no privileged language, and English is the
project's neutral choice for a supra-national layer (as for the COLREG layer).
"""

from __future__ import annotations

import re

# Canonical theme ids (stable keys) -> human label.
THEMES: dict[str, str] = {
    "scope_definitions": "Scope and definitions",
    "craft_design": "Craft design categories and essential requirements",
    "emissions": "Exhaust and noise emissions",
    "ce_marking": "Conformity assessment, CE marking and notified bodies",
    "market_rules": "Free movement, economic operators and market surveillance",
    "vessel_certification": "Union inland navigation certificate and inspection",
    "qualifications": "Certificates of qualification and competence",
    # id deliberately not "general": that key is already the COLREG theme, and
    # theme ids are a single global namespace (see tests/test_countries.py).
    "final_provisions": "Delegation, penalties and final provisions",
}

# Every theme is covered by the ingested acts, so nothing is scaffolded ahead of
# a source here.
EXTENSION_THEMES: frozenset[str] = frozenset()

# (lo, hi, theme) article ranges, inclusive, per act. Read from each act's own
# article titles (Directive 2013/53/EU has 58, 2016/1629 has 40, 2017/2397 has 41).
_RANGES: dict[str, tuple[tuple[int, int, str], ...]] = {
    # Recreational Craft Directive — the one a recreational exam actually tests.
    "2013/53/EU": (
        (1, 3, "scope_definitions"),
        (4, 4, "craft_design"),          # "Essential requirements" -> Annex I
        (5, 13, "market_rules"),         # navigation provisions, free movement, operators
        (14, 20, "ce_marking"),          # presumption of conformity … CE marking
        (21, 22, "emissions"),           # exhaust (21) and noise (22)
        (23, 42, "ce_marking"),          # post-construction, notified bodies
        (43, 46, "market_rules"),        # Union market surveillance and safeguards
        (47, 58, "final_provisions"),
    ),
    # Technical requirements for inland waterway craft (the Union certificate).
    "(EU) 2016/1629": (
        (1, 3, "scope_definitions"),
        (4, 27, "vessel_certification"),
        (28, 40, "final_provisions"),
    ),
    # Recognition of professional qualifications in inland navigation — the act
    # that makes a Dutch, German or French inland certificate mutually valid.
    "(EU) 2017/2397": (
        (1, 3, "scope_definitions"),
        (4, 29, "qualifications"),
        (30, 41, "final_provisions"),
    ),
}

# Annexes, by act. Annex I of the Recreational Craft Directive is the essential
# requirements — including the design-category table (wind force / significant
# wave height) that every European exam asks about; its other annexes are the
# conformity-assessment apparatus.
_ANNEX_THEME: dict[str, str] = {
    "2013/53/EU|I": "craft_design",
    "2013/53/EU": "ce_marking",
    "(EU) 2016/1629": "vessel_certification",
    "(EU) 2017/2397": "qualifications",
}

# No \b before "(EU)": the char before the paren is a space, so a word
# boundary never matches there and the alternative would be dead.
_ACT = re.compile(r"(\(EU\)\s*\d{4}/\d{1,4}|\b\d{4}/\d{1,4}/[A-Z]{2,3})")
_ART = re.compile(r"\bart\.\s*(\d+)\b")
_ANNEX = re.compile(r"\bAnnex\s*([IVXLC\d]*)\s*$")


def _act_of(ref: str) -> str:
    m = _ACT.search(ref or "")
    return re.sub(r"\s+", " ", m.group(1)) if m else ""


def theme_for(ref: str) -> str | None:
    """The theme a language-neutral EUR-Lex ref maps to, or None if it isn't one."""
    act = _act_of(ref)
    if not act:
        return None
    m = _ANNEX.search(ref)
    if m:
        return (_ANNEX_THEME.get(f"{act}|{m.group(1).upper()}")
                or _ANNEX_THEME.get(act))
    m = _ART.search(ref)
    if not m:
        return None
    n = int(m.group(1))
    for lo, hi, theme in _RANGES.get(act, ()):
        if lo <= n <= hi:
            return theme
    return None


def tag_theme(ref: str = "", title: str = "", text: str = "",
              default: str | None = None) -> str:
    """Return the EU theme id for a unit — by its act + article/annex number."""
    theme = theme_for(ref or "")
    if theme:
        return theme
    if default and default in THEMES:
        return default
    return "final_provisions"


def is_valid(theme_id: str) -> bool:
    return theme_id in THEMES
