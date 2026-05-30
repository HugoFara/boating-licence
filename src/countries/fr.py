"""France — the *permis plaisance* (recreational motor-boat licence).

Like :mod:`countries.ch`, this is a thin descriptor that reuses the France content
modules in :mod:`src.fr` (themes, exam profiles, legal sources) rather than
re-declaring them. France is **seed-driven**: it does not use the Fedlex-style
fetch pipeline, so `sources` is empty and the primary law is recorded as
`references` (each question carries its provenance inline — see `src/fr/seed_fr.py`).

French official acts carry no copyright and Légifrance / data.gouv.fr publish under
the Licence Ouverte / Etalab, so the whole bank is freely reusable — the France
analogue of the Swiss public-domain basis. Build it with `python run.py fr`.
"""

from __future__ import annotations

from .base import Country, Permit, ExamRules, Region, Reference
from ..fr import themes_fr, exam_fr

LEGAL_BASIS = (
    "Les actes officiels français (lois, décrets, arrêtés) sont exclus du droit "
    "d'auteur ; Légifrance / data.gouv.fr publient sous Licence Ouverte / Open "
    "Licence 2.0 (Etalab). Réutilisation libre, commerciale et non commerciale, "
    "avec attribution."
)

# The national exam format, identical for both base options (Arrêté du 28 sept.
# 2007, art. 1 & 2): 40 single-answer QCM, pass at ≤5 errors (35/40), ~30 min.
def _exam() -> ExamRules:
    return ExamRules(
        questions=exam_fr.QUESTIONS, time_limit_min=exam_fr.TIME_LIMIT_MIN,
        scoring="all_or_nothing", pass_points=exam_fr.PASS_POINTS,
        points_per_question=exam_fr.POINTS_PER_QUESTION,
        total_points=exam_fr.TOTAL_POINTS,
        note="40 QCM à réponse unique ; réussite : 5 fautes maximum (35/40) ; "
             "épreuve valable 18 mois. Examen national, sans variance régionale.")


# Sources are documented but not ingested (France is seed-driven); recorded so the
# legal finding lives in code. Includes the two extensions, which have no QCM bank.
REFERENCES: tuple[Reference, ...] = (
    Reference(
        name="Arrêté du 28 septembre 2007 (permis plaisance — référentiel)",
        url="https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000428843/",
        note="Définit le programme des options côtière (art. 1) et eaux "
             "intérieures (art. 2). Acte officiel, Licence Ouverte."),
    Reference(
        name="Décret n° 2007-1167 du 2 août 2007",
        url="https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000648362/",
        note="Cadre du permis plaisance (puissance > 4,5 kW, âge 16 ans)."),
    Reference(
        name="RIPAM — Règlement international pour prévenir les abordages en mer",
        url="https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000305722/",
        note="Règles de barre, feux et signaux (option côtière)."),
    Reference(
        name="Règlement général de police de la navigation intérieure (RGP/RGPNI)",
        url="https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000023086525/LEGISCTA000027232795/",
        note="Implémentation française du CEVNI (option eaux intérieures)."),
    Reference(
        name="Banques de questions des opérateurs agréés (La Poste, Dekra, SGS, "
             "Bureau Veritas)",
        url="https://www.mer.gouv.fr/le-permis-plaisance-permis-de-conduire-les-bateaux-de-plaisance-moteur",
        note="QCM officiels exploités sous contrat confidentiel depuis juin 2022 — "
             "NON réutilisables, jamais ingérés. Les questions du projet sont "
             "dérivées des textes de loi ci-dessus."),
    Reference(
        name="Extension hauturière / Extension grande plaisance eaux intérieures",
        url="https://www.mer.gouv.fr/le-permis-plaisance-permis-de-conduire-les-bateaux-de-plaisance-moteur",
        note="Hauturière : épreuve de carte (pas un QCM). Grande plaisance "
             "(> 20 m) : épreuve pratique. Aucune des deux n'a de banque QCM."),
)


def _tagger(ref: str = "", title: str = "", text: str = "",
            default: str | None = None) -> str:
    """France questions are pre-tagged at authoring time (each seed entry carries
    its theme), so there is no fetch-time tagging to do; return the default."""
    return default or "reglementation"


PERMITS: dict[str, Permit] = {
    "cotiere": Permit(
        code="cotiere", label="Permis plaisance — option côtière",
        themes=themes_fr.OPTION_THEMES["cotiere"], exam=_exam(), drive="motor",
        note="Mer, jusqu'à 6 milles nautiques d'un abri, de jour comme de nuit."),
    "eaux_interieures": Permit(
        code="eaux_interieures", label="Permis plaisance — option eaux intérieures",
        themes=themes_fr.OPTION_THEMES["eaux_interieures"], exam=_exam(), drive="motor",
        note="Rivières, canaux et lacs (RGP, implémentation CEVNI)."),
}

# The French exam is national — no regional variance (unlike the Swiss cantons).
REGIONS: dict[str, Region] = {
    "national": Region(code="national", name="National (France)", primary=True,
                       note="Examen national identique partout ; opérateurs agréés."),
}
DEFAULT_REGION = "national"


COUNTRY = Country(
    code="FR",
    name="France",
    default_lang="fr",
    langs=("fr", "en"),
    sources=(),                       # seed-driven; provenance is inline in the seed
    themes=dict(themes_fr.FR_THEMES),
    tagger=_tagger,
    permits=PERMITS,
    regions=REGIONS,
    default_region=DEFAULT_REGION,
    references=REFERENCES,
    legal_basis=LEGAL_BASIS,
)
