"""Switzerland — the project's original scope, re-expressed as a Country.

This is a thin adapter: it reuses the existing flat modules unchanged
(:mod:`src.sources`, :mod:`src.themes`, :mod:`src.cantons`, the cat-A/D profiles
in :mod:`src.questions.schema`) so CH behaviour is identical to before the
country dimension existed. Nothing here duplicates logic — it only repackages
those modules into the :class:`Country` shape the pipeline now reads.
"""

from __future__ import annotations

from .. import cantons, sources, themes
from ..questions import schema
from .base import Country, ExamRules, Permit, Region


def _exam(cfg: "schema.ExamConfig") -> ExamRules:
    return ExamRules(
        questions=cfg.questions, time_limit_min=cfg.time_limit_min,
        scoring=cfg.scoring, pass_points=cfg.pass_points,
        points_per_question=cfg.points_per_question, total_points=cfg.total_points)


_REGIONS = {
    c.code: Region(code=c.code, name=c.name, time_limit_min=c.time_limit_min,
                   primary=c.leman, note=c.note)
    for c in cantons.CANTONS.values()
}

_PERMITS = {
    code: Permit(code=cfg.permis, label=cfg.label, themes=tuple(cfg.themes),
                 exam=_exam(cfg), drive=("sail" if code == "D" else "motor"))
    for code, cfg in schema.PROFILES.items()
}


COUNTRY = Country(
    code="CH",
    name="Suisse / Schweiz / Svizzera",
    default_lang="fr",
    langs=("fr", "de", "it", "en"),
    sources=tuple(sources.SOURCES),
    themes=dict(themes.THEMES),
    tagger=themes.tag_theme,
    extension_themes=themes.EXTENSION_THEMES,
    permits=_PERMITS,
    regions=_REGIONS,
    default_region=cantons.DEFAULT_CANTON,
    legal_basis=("Public-domain federal/cantonal law (URG/LDA Art. 5) + openly "
                 "licensed references; theory exam standardised intercantonally "
                 "by the VKS."),
)
