"""Jurisdictions — the descriptive regime layer over the country registry.

`src/countries` is the *operational* layer: what the fetch→parse→normalize→
questions pipeline needs (sources, taggers, exam rules, permits, regions). This
module is the thin *descriptive* layer on top, and it earns its place by holding
two things a `Country` structurally cannot:

  1. **The CEVNI relation.** "Does this regime implement the harmonised European
     inland-navigation code (CEVNI)?" is the single fact that decides whether a
     regime's signage is portable into the shared core. It is recorded here once
     and read by :mod:`src.cevni` (the question classifier) and any manifest —
     rather than being assumed in scattered places.
  2. **Regimes that are not countries.** A `Country` cannot model **CEVNI itself**
     (a supra-national code) or **Lake Constance / Bodensee** (a tri-national
     shared lake governed by its own Bodensee-Schifffahrts-Ordnung, *outside*
     CEVNI). A `Jurisdiction` can, via `kind`.

It is **derived, not duplicated**: every country jurisdiction reads its display
data from `src.countries` (`derives_from`), so there is one source of truth for
names/codes and no drift. Adding a country to `src/countries` adds its
jurisdiction automatically; only genuinely supra/sub-national regimes are
declared here by hand.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from . import countries

# What kind of regime a jurisdiction is.
KINDS = {"country", "shared_water", "supra_national"}

# A regime's relation to CEVNI — the portability fact src.cevni reads.
#   implements — national law that enacts CEVNI; its harmonised signage IS core.
#   excluded   — explicitly outside CEVNI (Bodensee/BSO); signage NOT portable.
#   is_cevni   — the code itself (the shared core).
RELATIONS = {"implements", "excluded", "is_cevni", "unknown"}

# Per-country override; every inland regime modelled so far enacts CEVNI, so the
# default is "implements" and this stays empty until a non-CEVNI country appears.
_COUNTRY_RELATION: dict[str, str] = {}

DEFAULT = countries.DEFAULT


@dataclass(frozen=True)
class Jurisdiction:
    code: str                       # ISO country code, or a regime code (CEVNI, BODENSEE)
    name: str
    kind: str                       # one of KINDS
    cevni_relation: str             # one of RELATIONS
    members: tuple[str, ...] = ()   # for shared_water: the sharing countries
    derives_from: str = ""          # the src.countries code this draws display data from
    note: str = ""


def _build() -> dict[str, Jurisdiction]:
    reg: dict[str, Jurisdiction] = {}
    # Country jurisdictions, derived from the operational registry (no duplication).
    for code in countries.codes():
        c = countries.get(code)
        reg[c.code] = Jurisdiction(
            code=c.code, name=c.name, kind="country",
            cevni_relation=_COUNTRY_RELATION.get(c.code, "implements"),
            derives_from=c.code)
    # The shared core itself.
    reg["CEVNI"] = Jurisdiction(
        code="CEVNI", name="CEVNI — European code for inland waterways",
        kind="supra_national", cevni_relation="is_cevni",
        note="UNECE harmonised inland-navigation code; the cross-country core.")
    # A non-CEVNI shared-water regime. Its permits live on the German country
    # module; the jurisdiction records that its signage is NOT portable.
    reg["BODENSEE"] = Jurisdiction(
        code="BODENSEE", name="Lac de Constance / Bodensee",
        kind="shared_water", cevni_relation="excluded", members=("CH", "DE", "AT"),
        note="Bodensee-Schifffahrts-Ordnung (BSO); outside CEVNI — its signage is "
             "not portable into the European core.")
    return reg


REGISTRY: dict[str, Jurisdiction] = _build()


def get(code: str | None) -> Jurisdiction:
    """Return the Jurisdiction for a code (case-insensitive); defaults when empty,
    raises on an unknown non-empty code."""
    if not code:
        return REGISTRY[DEFAULT]
    key = code.upper()
    if key not in REGISTRY:
        raise ValueError(f"unknown jurisdiction {code!r}; choose from {sorted(REGISTRY)}")
    return REGISTRY[key]


def codes() -> list[str]:
    """All jurisdiction codes: the countries first (default first), then the
    non-country regimes (CEVNI, shared waters)."""
    country = [c for c in REGISTRY if REGISTRY[c].kind == "country"]
    country.sort(key=lambda c: (c != DEFAULT, c))
    other = sorted(c for c in REGISTRY if REGISTRY[c].kind != "country")
    return country + other


def relation(code: str) -> str:
    """The CEVNI relation of a jurisdiction (its portability fact)."""
    return get(code).cevni_relation


# --- the Bodensee (CEVNI-excluded) guard --------------------------------------
# Markers that tie a question to a CEVNI-excluded regime. Today only Lake
# Constance (BSO); extend as other excluded regimes are modelled. Kept here, not
# in src.cevni, because "which regimes are outside CEVNI" is a jurisdiction fact.
_EXCLUDED_MARKERS: dict[str, re.Pattern[str]] = {
    "BODENSEE": re.compile(
        r"\b(bodensee|bso|bodensee-schifffahrts|lac de constance|"
        r"lago di costanza)\b", re.I),
}


def excluded_regime(text: str) -> str | None:
    """If `text` (a question's ref/source/stem) ties it to a CEVNI-excluded
    regime, return that jurisdiction code (e.g. 'BODENSEE'); else None. Used by
    src.cevni to keep non-portable signage out of the European core."""
    for code, pat in _EXCLUDED_MARKERS.items():
        if pat.search(text or ""):
            return code
    return None


def as_manifest() -> list[dict]:
    """The descriptive table for a player/regime picker, in `codes()` order."""
    return [{
        "code": j.code, "name": j.name, "kind": j.kind,
        "cevni_relation": j.cevni_relation, "members": list(j.members),
        "derives_from": j.derives_from, "note": j.note,
    } for j in (REGISTRY[c] for c in codes())]
