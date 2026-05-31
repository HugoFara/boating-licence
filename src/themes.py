"""The 6 official exam themes and the rules for tagging knowledge units to them.

The taxonomy is the normalization target: every knowledge unit ends up tagged to
exactly one theme so Phase 2 can balance question selection the way the real exam
does. Tagging is deliberately simple and auditable (source defaults + keyword
heuristics over the unit's ref/title/text) — never a black box.
"""

from __future__ import annotations

import re
import unicodedata

# Canonical theme ids (stable keys) -> human label (French, as on the exam).
# The first six are the cat-A (motorboat) exam core. `voile` is appended last so
# the existing ids keep their index/order; it is the cat-D (sailing) extension
# theme — see PERMIS_THEMES and EXTENSION_THEMES below.
THEMES: dict[str, str] = {
    "definitions": "Définitions",
    "meteorologie": "Météorologie",
    "lois": "Lois sur la navigation en eaux intérieures",
    "signalisation": "Signalisation et signaux acoustiques",
    "matelotage": "Matelotage",
    "eaux_frontalieres": "Eaux frontalières",
    "voile": "Navigation à voile",
}

# Which themes each recreational-permit exam draws from. Cat-A (bateau à moteur)
# is the six-theme core the rest of the project is grounded in; cat-D (voile)
# shares that whole core and ADDS the sailing-theory theme on top. This is the
# single source of truth for the per-permit theme set (ExamConfig reads it).
PERMIS_THEMES: dict[str, tuple[str, ...]] = {
    "A": ("definitions", "meteorologie", "lois", "signalisation",
          "matelotage", "eaux_frontalieres"),
    "D": ("definitions", "meteorologie", "lois", "signalisation",
          "matelotage", "eaux_frontalieres", "voile"),
}

# Extension themes: present in a permit's theme set but NOT part of the official
# theory exam. `voile` (sailing technique — points of sail, tacking/gybing, rig,
# capsize) is study content for the cat-D *practical*; the cat-A/cat-D theory paper
# is identical and excludes it. It is grounded in the dedicated voile_wp Wikipedia
# sources (pin_theme="voile"; see src/sources.py) — no public-domain law defines
# sailing technique — and the player surfaces it as a study-only domain for cat-D,
# kept out of exam-mode draws. The normalize stage also excuses these from its
# "missing theme" warning so a build with no voile source still stays clean.
EXTENSION_THEMES: frozenset[str] = frozenset({"voile"})

# Keyword heuristics, evaluated in priority order. The first theme whose pattern
# matches the unit's searchable text wins, unless the unit carries an explicit
# theme already (e.g. a prose source pinned by its parser).
# A terminology article announces itself *structurally*, and we detect it before
# the keyword rules so it isn't stolen by the generic signalisation match (a
# definitions list naturally enumerates signal/buoy/light terms). Two anchored
# signals, both high-precision:
#  - the *title* ends in "Définition(s)" or is "Signification de quelques termes"
#    (ONI art. 2, RNL art. 1, ONI art. 61/142);
#  - the *text* opens with the canonical definitional lead-in.
# Anchoring matters: it keeps genuine signalisation articles that merely *contain*
# an inline definition (e.g. RNL art. 46 "on entend par: un son bref…") out.
_DEF_TITLE = re.compile(
    r"(^\s*d[eé]finitions?\b|d[eé]finitions?\s*$|"
    r"signification de (quelques )?termes\s*$)", re.I)
_DEF_TEXT_START = re.compile(
    r"^\s*(\d+\s*)?(dans (la pr[eé]sente (ordonnance|convention)|"
    r"le pr[eé]sent r[eè]glement)\s*:|au sens de la pr[eé]sente)", re.I)


def _is_definitions(title: str, text: str) -> bool:
    return bool(_DEF_TITLE.search(title or "")) or \
        bool(_DEF_TEXT_START.match((text or "").lstrip()))


_RULES: list[tuple[str, re.Pattern[str]]] = [
    # Storm-warning signals are a Météorologie exam topic, not Signalisation —
    # this narrow rule runs first so "avis de tempête / fort vent / feux d'alerte"
    # wins over the generic signal/feux match below. Buoy & light signs (which
    # never use this wording) stay in Signalisation.
    ("meteorologie", re.compile(
        r"(avis de (fort )?vent|avis de temp[eê]te|signaux d.avis|"
        r"signaux de temp[eê]te|feux d.alerte|signaux de fort vent)")),
    ("signalisation", re.compile(
        r"\b(signal|signalisation|signaux|balis|bou[eé]e|feu[x]?|pavillon|"
        r"acoustique|sonore|marque|panneau)\b")),
    # Note: bare "vent" is deliberately NOT a keyword — it false-matches
    # "bateaux à voile" right-of-way rules and "surface vélique". Real météo is
    # caught by the storm rule above, the named winds here, and source defaults
    # (the MétéoSuisse "Le Vent" sections fall back to their meteorologie default).
    ("meteorologie", re.compile(
        r"\b(m[eé]t[eé]o|bise|joran|vaudaire|bornan|s[eé]chard|temp[eê]te|"
        r"orage|rafale|nu[ae]ge|grain)\b")),
    ("matelotage", re.compile(
        r"\b(matelotage|n[oœ]ud|amarr|mouillage|ancre|cordage|bitte|taquet|"
        r"demi-cl[eé]|chaise)\b")),
    # NB: there is no keyword rule for `voile`. Sailing-technique vocabulary
    # (surface vélique, gréement, gîte, vent arrière, allures…) also appears in the
    # *law* — ONI art. 79 defines the cat-D permit by "surface vélique > 15 m²",
    # art. 134/137/153 mention gréement/gîte — so any keyword rule mis-tags those
    # articles as voile and pulls them out of `lois`. `voile` is therefore a
    # PIN-ONLY theme: only the dedicated voile_wp Wikipedia sources (pin_theme=
    # "voile") carry it; law text keeps its proper theme. See PERMIS_THEMES /
    # EXTENSION_THEMES above and src/sources.py.
    ("eaux_frontalieres", re.compile(
        r"\b(l[eé]man|fronti[eè]re|franco-suisse|france|eaux fronta)\b")),
    # Note: there is no loose "definitions" keyword rule. A bare "définition" /
    # "au sens de la présente" / "on entend par" fires inside procedural articles
    # that merely *cite* a definition (e.g. ONI art. 84/91b on permits). Real
    # terminology articles are caught up-front by the anchored _is_definitions().
]


def _norm(text: str) -> str:
    """Lowercase; keep accents (rules match accented or not via [eé] classes)."""
    return (text or "").lower()


def tag_theme(ref: str = "", title: str = "", text: str = "",
              default: str | None = None) -> str:
    """Return the best theme id for a unit. `default` (a source-level hint) is
    used as a fallback and also wins ties when no keyword rule fires."""
    # High-precision structural check first: a genuine terminology article goes to
    # Définitions even though its term list mentions signals, buoys, lights, etc.
    if _is_definitions(title, text):
        return "definitions"
    haystack = _norm(" ".join((ref, title, text)))
    for theme_id, pattern in _RULES:
        if pattern.search(haystack):
            return theme_id
    if default and default in THEMES:
        return default
    # Sensible last resort: law text with no stronger signal is "lois".
    return "lois"


# Themes contributed by other countries' content modules. Switzerland's six-theme
# core (above) is the project's grounded default and the tagging target; other
# jurisdictions (e.g. France, src/fr/themes_fr.py) have their own exam taxonomies
# that don't share these ids. They register here on import so question validation
# (`is_valid`) accepts them, without this module having to import or know about
# them. Empty on a stock Swiss build — no behaviour change there.
_REGISTERED: dict[str, str] = {}


def register_themes(mapping: dict[str, str]) -> None:
    """Register a country's theme ids → labels so validation accepts them. Additive
    and idempotent; ids are global, so countries must keep them distinct."""
    _REGISTERED.update(mapping)


def label(theme_id: str) -> str:
    """Human label for a theme id, across the Swiss core and any registered set."""
    return THEMES.get(theme_id) or _REGISTERED.get(theme_id, theme_id)


def is_valid(theme_id: str) -> bool:
    return theme_id in THEMES or theme_id in _REGISTERED
