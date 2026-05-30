"""French *permis plaisance* exam profiles.

Reuses the canonical `schema.ExamConfig` so the build's meta-stamping and the
player consume France exactly like Switzerland — only the values differ. The
French exam is **national** (no cantonal variance), so the `canton_*` fields are
repurposed to a single "National (France)" descriptor and the player, seeing one
region, hides its region picker.

Both base options share the format set by the Arrêté du 28 septembre 2007:
**40 questions, pass at ≤5 errors (35/40), ~30 min**. In the point model that is
40 × 1 pt, pass 35, all-or-nothing. Validity of a passed theory exam: 18 months.
"""

from __future__ import annotations

from ..questions.schema import ExamConfig
from . import themes_fr

# Shared national parameters (identical for côtière and eaux intérieures).
QUESTIONS = 40
POINTS_PER_QUESTION = 1
TOTAL_POINTS = QUESTIONS * POINTS_PER_QUESTION   # 40
PASS_POINTS = 35                                 # at most 5 errors
TIME_LIMIT_MIN = 30
REGION_LABEL = "National (France)"
REGION_CODE = "FR"

_LABELS = {
    "cotiere": "Permis plaisance — option côtière",
    "eaux_interieures": "Permis plaisance — option eaux intérieures",
}


def _profile(option: str) -> ExamConfig:
    return ExamConfig(
        questions=QUESTIONS, total_points=TOTAL_POINTS,
        points_per_question=POINTS_PER_QUESTION, pass_points=PASS_POINTS,
        time_limit_min=TIME_LIMIT_MIN, scoring="all_or_nothing",
        canton_default=REGION_LABEL, canton_code=REGION_CODE,
        permis=option, label=_LABELS[option],
        themes=themes_fr.OPTION_THEMES[option])


PROFILES: dict[str, ExamConfig] = {opt: _profile(opt) for opt in _LABELS}


def profile(option: str = "cotiere") -> ExamConfig:
    key = (option or "cotiere").lower()
    if key not in PROFILES:
        raise ValueError(f"unknown France option {option!r}; "
                         f"choose from {sorted(PROFILES)}")
    return PROFILES[key]
