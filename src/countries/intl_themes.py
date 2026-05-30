"""COLREG theme taxonomy + tagger for the international/harmonised layer.

The COLREGS base (``src.jurisdictions``) is grounded by the verbatim International
Regulations (1972), which are structured into named **Parts** by rule number:

    Part A — General                  Rules 1–3   (application, responsibility, definitions)
    Part B — Steering and Sailing     Rules 4–19  (look-out, give-way, overtaking…)
    Part C — Lights and Shapes        Rules 20–31
    Part D — Sound and Light Signals  Rules 32–37
    Part E — Exemptions               Rule 38
    Annexes I–V                       technical detail + distress signals

So the tagger is *deterministic*: a unit's COLREG rule (or annex) number maps to
exactly one theme — no keyword guessing for the canonical text. A keyword fallback
is kept only for robustness if a unit reaches the tagger without a parseable ref.
The labels are English because the only public-domain source is English (USCG); a
translation would be a modification, so this layer stays English-only (like the
German ELWIS bank stays German-only).
"""

from __future__ import annotations

import re

# Canonical theme ids (stable keys) -> human label. One per COLREG Part, plus the
# technical annexes. These ids never collide with the Swiss/German/French
# taxonomies, so a COLREG unit is recognised by its theme alone.
THEMES: dict[str, str] = {
    "general": "General — application, responsibility & definitions",
    "steering_sailing": "Steering and sailing rules",
    "lights_shapes": "Lights and shapes",
    "sound_light_signals": "Sound and light signals",
    "exemptions": "Exemptions",
    "annexes": "Technical annexes",
}

# Every theme is covered by the canonical text, so a COLREG-only build has no empty
# rule-bearing theme — nothing to scaffold here.
EXTENSION_THEMES: frozenset[str] = frozenset()

# COLREG Part boundaries by rule number (inclusive). Order matters only for the
# final catch-all; lookup is by range.
_PART_BY_RULE: tuple[tuple[int, int, str], ...] = (
    (1, 3, "general"),
    (4, 19, "steering_sailing"),
    (20, 31, "lights_shapes"),
    (32, 37, "sound_light_signals"),
    (38, 38, "exemptions"),
)


def theme_for_rule(n: int) -> str:
    """The theme for COLREG Rule ``n`` (1–38), by its Part."""
    for lo, hi, theme in _PART_BY_RULE:
        if lo <= n <= hi:
            return theme
    return "general"


_RULE_REF = re.compile(r"\brule\s+(\d+)\b", re.I)
_ANNEX_REF = re.compile(r"\bannex(es)?\b", re.I)

# Keyword fallback — only used when a unit arrives without a parseable rule/annex
# ref (the canonical parser always supplies one, so this is belt-and-braces).
_KEYWORDS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("sound_light_signals", re.compile(
        r"\b(sound signal|whistle|fog signal|bell|gong|manoeuvr\w* signal)\b", re.I)),
    ("lights_shapes", re.compile(
        r"\b(light|shape|all-round|sidelight|sternlight|masthead|cylinder|cone|ball)\b", re.I)),
    ("steering_sailing", re.compile(
        r"\b(look-?out|safe speed|risk of collision|overtak\w*|give-way|stand-on|"
        r"crossing|head-on|narrow channel|traffic separation)\b", re.I)),
    ("general", re.compile(
        r"\b(application|responsib\w*|definition|vessel means)\b", re.I)),
)


def tag_theme(ref: str = "", title: str = "", text: str = "",
              default: str | None = None) -> str:
    """Return the COLREG theme id for a unit. Deterministic by the rule/annex
    number in ``ref`` (the canonical case); a keyword scan + ``default`` are the
    fallbacks for units lacking a parseable ref."""
    m = _RULE_REF.search(ref or "") or _RULE_REF.search(title or "")
    if m:
        return theme_for_rule(int(m.group(1)))
    if _ANNEX_REF.search(ref or "") or _ANNEX_REF.search(title or ""):
        return "annexes"
    haystack = " ".join((ref, title, text)).lower()
    for theme_id, pattern in _KEYWORDS:
        if pattern.search(haystack):
            return theme_id
    if default and default in THEMES:
        return default
    return "general"


def is_valid(theme_id: str) -> bool:
    return theme_id in THEMES
