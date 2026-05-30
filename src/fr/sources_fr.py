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
        "IALA — Système de balisage maritime, région A (Recommandation R1001)",
        "https://www.iala-aism.org/product/r1001-maritime-buoyage-system-mbs/",
        licence="IALA R1001 — standard international ; contenu factuel (couleurs, "
                "voyants, marques) librement citable.",
    ),
    "division_245": FrSource(
        "division_245",
        "Division 245 (arrêté du 10 février 2016) — matériel d'armement et de "
        "sécurité des bateaux de plaisance en eaux intérieures",
        "https://www.legifrance.gouv.fr/loda/id/JORFTEXT000032036538/",
    ),
    "directive_2013_53": FrSource(
        "directive_2013_53",
        "Directive 2013/53/UE relative aux bateaux de plaisance — catégories de "
        "conception (annexe I, partie A)",
        "https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32013L0053",
        licence="© Union européenne, eur-lex.europa.eu — réutilisation autorisée "
                "(décision 2011/833/UE).",
    ),
    "itu_rr": FrSource(
        "itu_rr",
        "UIT — Règlement des radiocommunications (canaux VHF maritimes, procédures "
        "de détresse et d'urgence)",
        "https://www.itu.int/pub/R-REG-RR",
        licence="UIT — canaux et procédures internationaux ; contenu factuel "
                "librement citable.",
    ),
    "code_transports": FrSource(
        "code_transports",
        "Code des transports — navigation intérieure (titre de navigation, "
        "alcoolémie, règlements particuliers de police)",
        "https://www.legifrance.gouv.fr/codes/texte_lc/LEGITEXT000023086525/",
    ),
    "code_environnement": FrSource(
        "code_environnement",
        "Code de l'environnement — pollution par les rejets des navires "
        "(art. L.218-11 et s.) / convention MARPOL",
        "https://www.legifrance.gouv.fr/codes/texte_lc/LEGITEXT000006074220/",
    ),
    "prefet_maritime": FrSource(
        "prefet_maritime",
        "Arrêtés des préfets maritimes (bande littorale des 300 m ; mouillage et "
        "protection de la posidonie)",
        "https://www.premar-mediterranee.gouv.fr/",
    ),
    "shom": FrSource(
        "shom",
        "SHOM — Service hydrographique et océanographique de la marine (cartes et "
        "marées : zéro hydrographique, marnage, coefficient, étale)",
        "https://www.shom.fr/",
        licence="SHOM — données et références hydrographiques officielles "
                "(réutilisation sous Licence Ouverte / Etalab).",
    ),
    "meteo_france": FrSource(
        "meteo_france",
        "Météo-France / OMM — échelle de Beaufort (force 0 à 12)",
        "https://meteofrance.com/",
        licence="Échelle de Beaufort (OMM) — barème international du domaine public.",
    ),
    "cevni": FrSource(
        "cevni",
        "CEVNI — Code européen des voies de navigation intérieure (CEE-ONU, "
        "Résolution n° 24)",
        "https://unece.org/transport/inland-water-transport",
        licence="CEE-ONU — code européen modèle, librement consultable.",
    ),
}


def get(source_id: str) -> FrSource:
    if source_id not in FR_SOURCES:
        raise ValueError(f"unknown FR source {source_id!r}; "
                         f"choose from {sorted(FR_SOURCES)}")
    return FR_SOURCES[source_id]
