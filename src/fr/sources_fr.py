"""Primary legal sources for the French *permis plaisance* question bank.

Unlike the Swiss sources (`src.sources`), these are not fetched: the seed bank
(`seed_fr.py`) is hand-authored and carries each question's provenance inline by
referencing one of these source ids. Every source is a French official act or an
openly-licensed public-sector reference, so the whole bank is freely reusable —
the France analogue of the Swiss public-domain basis.

French official acts (laws, decrees, *arrêtés*) are excluded from copyright, and
Légifrance / data.gouv.fr content is published under the **Licence Ouverte / Open
Licence 2.0 (Etalab)**: free reuse, commercial and non-commercial, with attribution.
"""

from __future__ import annotations

from dataclasses import dataclass

_OPEN = ("Licence Ouverte / Open Licence 2.0 (Etalab) — French official act, "
         "freely reusable with attribution.")


@dataclass(frozen=True)
class FrSource:
    id: str          # stable id, referenced by seed entries
    name: str        # human label (carried into provenance.source)
    url: str         # canonical reference URL
    licence: str = _OPEN
    as_of: str = ""  # legal version / consolidation date, when relevant


FR_SOURCES: dict[str, FrSource] = {
    "arrete_2007": FrSource(
        "arrete_2007",
        "Arrêté du 28 septembre 2007 relatif au permis de conduire des bateaux "
        "de plaisance à moteur (référentiel)",
        "https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000428843/",
        as_of="2022-06-01",
    ),
    "decret_2007": FrSource(
        "decret_2007",
        "Décret n° 2007-1167 du 2 août 2007 relatif au permis de conduire des "
        "bateaux de plaisance à moteur",
        "https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000648362/",
    ),
    "ripam": FrSource(
        "ripam",
        "RIPAM — Règlement international pour prévenir les abordages en mer "
        "(COLREG 1972)",
        "https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000305722/",
    ),
    "rgp": FrSource(
        "rgp",
        "Règlement général de police de la navigation intérieure (RGP/RGPNI) — "
        "Code des transports, art. R. 4241-1 et s.",
        "https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000023086525/LEGISCTA000027232795/",
    ),
    "division_240": FrSource(
        "division_240",
        "Division 240 — matériel de sécurité des navires de plaisance de moins "
        "de 24 mètres",
        "https://www.mer.gouv.fr/la-division-240",
    ),
    "iala_a": FrSource(
        "iala_a",
        "Balisage maritime — système IALA région A (référentiel permis plaisance)",
        "https://www.mer.gouv.fr/le-permis-plaisance-permis-de-conduire-les-bateaux-de-plaisance-moteur",
    ),
}


def get(source_id: str) -> FrSource:
    if source_id not in FR_SOURCES:
        raise ValueError(f"unknown FR source {source_id!r}; "
                         f"choose from {sorted(FR_SOURCES)}")
    return FR_SOURCES[source_id]
