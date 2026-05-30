"""CEVNI-core classification: which questions are portable across countries.

National inland-navigation rules are national implementations of **CEVNI** (the
UNECE *Code Européen des Voies de Navigation Intérieure*). The signs, buoyage,
lights and sound signals it harmonises are identical across signatory states — a
lateral mark or a "no entry" board is the same in CH, DE, FR or NL — so a question
that tests them is reusable everywhere; only its legal *citation* re-grounds per
country. National statute (permits, frontier conventions) and water-body specifics
(a named local wind, a lake's storm-signal rates) are **not** portable.

This module assigns each `Question` a `scope`:

  * ``cevni``    — harmonised CEVNI content (signs, navigation rules, generic
                   seamanship / meteorology / definitions). The shared core.
  * ``national`` — country statute: permit/administration law, bilateral frontier
                   rules. Belongs to one country.
  * ``local``    — tied to a specific water body: named Léman winds, lake-specific
                   storm-signal operation.

The classification is **derived, never stored** — it is computed at export time
from the question's theme + ref/source/stem, so the schema and the per-language
bundles are untouched (they stay byte-identical). It is a deliberately auditable
heuristic (every rule names itself, like `src.themes`), and a *starting point*: a
country-agent tunes the keyword sets below for their own law. The default leans
``cevni`` because the harmonised signage is the bulk of every bank.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from . import jurisdictions

if TYPE_CHECKING:                      # avoid any import cycle; we only duck-type
    from .questions.schema import Question

SCOPES = {"cevni", "national", "local"}
DEFAULT_SCOPE = "cevni"

# Within `lois`: country *statute* (permits, registration, insurance, sanctions)
# rather than the CEVNI navigation rules. Country-specific → national.
_NATIONAL_ADMIN = re.compile(
    r"\b(permis|autoris\w*|immatricul\w*|assuranc\w*|attestation|certificat|"
    r"plaque|taxe|redevance|registre|examen|sanction|amende|retrait|"
    r"responsabilit\w*|ofrou|ocv|office cantonal)\b", re.I)

# Within `meteorologie`: tied to Lac Léman specifically (named local winds, or the
# lake's storm-warning signal operation) → local. Generic weather stays cevni.
_LOCAL_METEO = re.compile(
    r"\b(l[eé]man|bise|joran|vaudaire|bornan|s[eé]chard|morget|rebat|molan|"
    r"s[uû]dois|vauderon|avis de (fort )?vent|avis de temp[eê]te|"
    r"feux d.alerte|scintillant)\b", re.I)

# Bilateral / frontier wording that pins even a non-eaux_frontalieres question to a
# specific country pairing → national.
_FRONTIER = re.compile(r"\b(franco-suisse|eaux fronta|convention.*france|"
                       r"accord.*france)\b", re.I)


def _haystack(q: "Question") -> str:
    p = q.provenance
    return " ".join((q.stem or "", getattr(p, "ref", "") or "",
                     getattr(p, "source", "") or "")).lower()


def classify(q: "Question") -> str:
    """Return the CEVNI scope of a question: ``cevni`` | ``national`` | ``local``.

    Theme is the primary signal, refined by the keyword sets above. Auditable:
    the branch a question takes is determined entirely by its theme + the regexes,
    so a country-agent can read and tune it.
    """
    text = _haystack(q)
    theme = q.theme

    # CEVNI-excluded regime guard (e.g. Lake Constance / BSO): its signage is NOT
    # harmonised, so it can never enter the European core whatever its theme. The
    # list of excluded regimes is a jurisdiction fact (src.jurisdictions).
    if jurisdictions.excluded_regime(text):
        return "local"

    # Bilateral frontier waters are inherently country-pair-specific.
    if theme == "eaux_frontalieres" or _FRONTIER.search(text):
        return "national"

    # Weather: lake-specific named winds / storm signals are local; the rest
    # (cloud types, fronts, general wind) is portable knowledge.
    if theme == "meteorologie":
        return "local" if _LOCAL_METEO.search(text) else "cevni"

    # Navigation law: CEVNI rules are portable, but permit/registration/sanction
    # statute is national.
    if theme == "lois":
        return "national" if _NATIONAL_ADMIN.search(text) else "cevni"

    # Signalisation (harmonised signs/buoyage/lights/sound signals), matelotage,
    # definitions and voile are country-agnostic CEVNI core.
    return "cevni"


def core_bank(questions: list["Question"]) -> list["Question"]:
    """The ``cevni``-scoped subset — the shared, cross-country reusable core."""
    return [q for q in questions if classify(q) == "cevni"]


def scope_counts(questions: list["Question"]) -> dict[str, int]:
    """How many questions fall in each scope (for build summaries / audits)."""
    counts = {s: 0 for s in SCOPES}
    for q in questions:
        counts[classify(q)] += 1
    return counts
