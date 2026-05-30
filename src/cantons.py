"""Per-canton variance in the motorboat theory exam.

The theory exam is standardised intercantonally by the **VKS** (Vereinigung der
kantonalen Schifffahrtsämter): 60 questions, 180 points, pass at 165, and the
question *content* is the national standard. What an individual canton sets for
itself is small and well-bounded — chiefly the **time allowed** and which office
administers the test. The pass mark and question bank do not vary.

So this registry deliberately stays minimal: it encodes only values that are
actually verified, and anything not separately confirmed inherits the VKS
standard (`VKS_TIME_LIMIT_MIN`). That is the honest default — not a guess dressed
up as a cantonal fact.

It is the single source of truth for the variance: the build stamps a default
canton into the bank meta (`ExamConfig`), exports the table into
`languages.json`, and the player lets a learner pick their canton so the exam
timer matches theirs.
"""

from __future__ import annotations

from dataclasses import dataclass

# The intercantonal default the VKS standard uses; a canton may shorten it.
VKS_TIME_LIMIT_MIN = 50


@dataclass(frozen=True)
class Canton:
    """One canton's exam variance. `time_limit_min` is the only numeric the VKS
    leaves to the canton; everything else (count, points, pass mark, content) is
    the national standard carried by `ExamConfig`."""
    code: str                # ISO 3166-2 cantonal abbreviation (GE, VD, BE…)
    name: str                # human label
    time_limit_min: int      # minutes allowed for the 60-question paper
    leman: bool = False      # borders Lac Léman (the project's primary scope)
    note: str = ""           # short provenance / caveat (display-optional)


# The Swiss shore of Lac Léman is bordered by **Geneva and Vaud only** — Valais
# sits upstream in the Rhône valley and the south shore is French (Haute-Savoie),
# so neither adds a Léman canton. Bern is included as the documented 45-minute
# variant of the otherwise-50-minute VKS exam, even though it is not on the lake,
# because it is the one concrete time-limit difference we can cite.
CANTONS: dict[str, Canton] = {
    "GE": Canton("GE", "Genève", VKS_TIME_LIMIT_MIN, leman=True,
                 note="OCV — Office cantonal des véhicules; national VKS standard."),
    "VD": Canton("VD", "Vaud", VKS_TIME_LIMIT_MIN, leman=True,
                 note="National VKS standard."),
    "BE": Canton("BE", "Berne / Bern", 45,
                 note="Documented 45-minute variant of the VKS exam (not on the Léman)."),
}

# The project's primary scope is Geneva / OCV on the Léman.
DEFAULT_CANTON = "GE"


def get(code: str | None) -> Canton:
    """Return the Canton for a code (case-insensitive); falls back to the default
    when `code` is empty, raises on an unknown non-empty code."""
    if not code:
        return CANTONS[DEFAULT_CANTON]
    key = code.upper()
    if key not in CANTONS:
        raise ValueError(f"unknown canton {code!r}; choose from {sorted(CANTONS)}")
    return CANTONS[key]


def is_valid(code: str) -> bool:
    return bool(code) and code.upper() in CANTONS


def as_manifest() -> list[dict]:
    """The table the static player needs for its canton picker, in a stable order
    (Léman cantons first, then the rest)."""
    ordered = sorted(CANTONS.values(), key=lambda c: (not c.leman, c.code))
    return [{"code": c.code, "name": c.name, "time_limit_min": c.time_limit_min,
             "leman": c.leman, "note": c.note} for c in ordered]
