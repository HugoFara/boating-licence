"""What the Dutch klein-vaarbewijs exam is actually allowed to ask about.

*Binnenvaartregeling* art. 7.15 names the exam's subjects in five lines. The
**examenprogramma**, established by the Minister of Infrastructuur en Waterstaat
and published by the CBR in its *Examendocument Klein Vaarbewijs 1*, resolves
those five lines down to **named articles** of named acts — and that is what this
module records: the article numbers, per act, that the exam may draw on.

Why it is worth recording rather than drafting over the whole corpus: the Dutch
knowledge base holds 860 units, of which 556 are long enough to draft from, but
most of them (professional crewing rules, per-waterway name lists, certification
bureaucracy) can never appear on a recreational paper. Drafting blind would spend
most of the effort on questions no candidate will ever be asked. Scoped to the
programme, the same effort lands on the ~130 articles that carry the exam.

**What is reproduced here and what is not.** Only the *article numbers* — which
provisions are examinable, a set of facts, not anyone's expression — together
with the act they belong to. The CBR's own elaboration in that document (its
`afbakening` prose and its `toetsmatrijs` weighting tables) is NOT reproduced:
cbr.nl reserves its rights expressly ("Alle intellectuele eigendomsrechten worden
voorbehouden"), which switches off the default permission Auteurswet art. 15b
would otherwise give for a work published by a public authority. The underlying
exam programme is the Minister's, and a ministerial instrument carries no
copyright at all (Auteurswet art. 11).

Source: CBR, *Examendocument Klein Vaarbewijs 1*, chapter 1 (examenprogramma,
vastgesteld door de Minister van I&W) and the article citations in chapter 2.
https://www.cbr.nl/nl/service/nl/artikel/examendocument-kvb1 — read 2026-08-15.
"""

from __future__ import annotations

import re

# --- Klein Vaarbewijs I -------------------------------------------------------
# Keyed by the source id in :mod:`countries.nl`. Values are the provision numbers
# as the acts themselves write them ("6.04a", "35a", "785").

# The Binnenvaartpolitiereglement is the spine: chapters 1-10, ~100 articles.
_BPR_KVB1 = (
    # Ch. 1 — scope, definitions, duties of the schipper and crew
    "1.01", "1.02", "1.03", "1.04", "1.05", "1.06", "1.08", "1.09", "1.10",
    "1.11", "1.12", "1.13", "1.19", "1.20",
    # Ch. 2 — identification marks
    "2.02",
    # Ch. 3 — lights and day shapes
    "3.01", "3.01a", "3.03", "3.04", "3.07", "3.08", "3.09", "3.10", "3.11",
    "3.12", "3.13", "3.14", "3.15", "3.16", "3.18", "3.20", "3.25", "3.26",
    "3.27", "3.28", "3.29", "3.30", "3.31", "3.32", "3.34", "3.37", "3.38",
    # Ch. 4 — sound signals, radio
    "4.01", "4.02", "4.03", "4.05", "4.06",
    # Ch. 6 — the steering and sailing rules
    "6.01", "6.02", "6.02a", "6.03", "6.04", "6.04a", "6.05", "6.07", "6.09",
    "6.10", "6.13", "6.14", "6.15", "6.16", "6.17", "6.18", "6.19", "6.20",
    "6.23", "6.24", "6.25", "6.26", "6.28", "6.28a", "6.28b", "6.29", "6.30",
    "6.31", "6.32", "6.33",
    # Ch. 7 — berthing
    "7.01", "7.02", "7.03", "7.04", "7.07", "7.09", "7.10",
    # Ch. 8 — supplementary provisions (fast motorboats, small craft, waterskiing)
    "8.01", "8.02", "8.03", "8.04", "8.05", "8.06", "8.07", "8.08",
    # Ch. 9-10 — the special provisions that reach recreational traffic
    "9.01", "9.03", "9.04", "9.05", "9.07", "10.01", "10.03", "10.08",
)

# The Rhine regime, examined "in particular where it differs from the BPR".
_RPR_KVB1 = (
    "1.00", "1.01", "1.02", "1.03", "1.04", "1.05", "1.09", "1.11", "1.16",
    "3.13", "3.25", "6.01", "6.02", "6.02a", "6.04", "6.05", "6.07", "6.11",
    "6.12", "6.16", "6.17", "6.20", "6.23", "6.24", "6.28", "6.29", "6.30",
    "6.33", "8.03a", "8.05", "9.04",
)

# The statutory spine. Read from the programme's own citations: the alcohol limit
# and the withdrawal of a vaarbewijs (SVW), which vaarbewijs a craft needs and the
# minimum age (BVW/BVB), the duty to assist after a collision (WvK art. 785), and
# the BPR's area of application (its Vaststellingsbesluit art. 2).
SCOPE_KVB1: dict[str, tuple[str, ...]] = {
    "bpr": _BPR_KVB1,
    "rpr": _RPR_KVB1,
    "svw": ("27", "35a", "35b"),
    "binnenvaartwet": ("1", "25", "27"),
    "binnenvaartbesluit": ("1", "13", "14", "15", "16"),
    "wvk": ("785",),
    "vaststellingsbesluit_bpr": ("2",),
}

# Klein Vaarbewijs II is the KVB I material plus the sea-going frontier regimes
# (Scheepvaartreglement Westerschelde, Eemsmonding, Kanaal Gent-Terneuzen, and the
# international collision regulations) and the navigation/meteorology subjects.
# Those acts are not ingested yet, so the scope is declared empty rather than
# guessed — an empty scope means "not modelled", never "nothing is examinable".
SCOPE_KVB2: dict[str, tuple[str, ...]] = {}

# "Binnenvaartpolitiereglement Artikel 6.04a" -> ("Binnenvaartpolitiereglement", "6.04a")
_REF = re.compile(r"^(.*?)\s+Artikel\s+(\S+)$", re.I)

# ref prefix (the act's citeertitel) -> source id
_ACT_BY_TITLE = {
    "binnenvaartpolitiereglement": "bpr",
    "rijnvaartpolitiereglement 1995": "rpr",
    "scheepvaartverkeerswet": "svw",
    "binnenvaartwet": "binnenvaartwet",
    "binnenvaartbesluit": "binnenvaartbesluit",
    "wetboek van koophandel": "wvk",
    "vaststellingsbesluit binnenvaartpolitiereglement": "vaststellingsbesluit_bpr",
}


def source_of(ref: str) -> str:
    """The source id a KB ref belongs to ("" when it names no known act)."""
    m = _REF.match((ref or "").strip())
    if not m:
        return ""
    return _ACT_BY_TITLE.get(m.group(1).strip().lower(), "")


def examinable(ref: str, scope: dict[str, tuple[str, ...]] | None = None) -> bool:
    """Is this KB unit within the klein-vaarbewijs exam programme?

    Refs from an act the programme does not name at all (the Binnenvaartregeling's
    professional-crewing chapters, the territorial-sea reglement) are out, as are
    articles of a named act that the programme does not list.
    """
    scope = SCOPE_KVB1 if scope is None else scope
    m = _REF.match((ref or "").strip())
    if not m:
        return False
    src = _ACT_BY_TITLE.get(m.group(1).strip().lower(), "")
    return bool(src) and m.group(2) in scope.get(src, ())


def counts() -> dict[str, int]:
    """Examinable provisions per act — the drafting budget, at a glance."""
    return {k: len(v) for k, v in SCOPE_KVB1.items()}
