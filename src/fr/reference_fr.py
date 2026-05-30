"""Ingest the maritime *reference* corpus France's côtière content rests on:
the **IALA** Maritime Buoyage System (Region A) and **SHOM** tides/charts.

Unlike `legi.py` (verbatim French law from the Etalab LEGI dump), these sources
are **not** openly licensed for verbatim redistribution: IALA Recommendation R1001
is © IALA, and SHOM publications carry SHOM terms (its open *data* is Licence
Ouverte, but the ouvrages are not). What IS freely usable is the **factual
content** — the colour/shape/topmark/light of each buoyage mark, the definition of
the tidal datum, the coefficient range — which is not copyrightable. So we ingest
those facts, each **verified against and cited to the primary source** (the rule:
grounded, never recall), as `KnowledgeUnit`s — NOT copied prose.

Verified 2026-05-30 against: IALA R1001 Ed.2.0 (Tables 1–9, the official MBS) and
the SHOM *Prédiction de marée* fiche (refmar.shom.fr) + maree.shom.fr. This corpus
grounds the côtière themes (`balisage`, `meteo_maree`) the way `legi_kb.json`
grounds the inland ones.

    python -m src.fr.reference_fr build    # → data/kb.fr.sqlite + src/fr/reference_kb.json
"""

from __future__ import annotations

import datetime as _dt
import json
import os
from dataclasses import asdict

from ..schema import KnowledgeUnit, make_id, connect, write_units, set_meta
from . import sources_fr, themes_fr  # noqa: F401  (themes_fr registers FR themes)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
KB_DB = os.path.join(ROOT, "data", "kb.fr.sqlite")
REF_JSON = os.path.join(ROOT, "src", "fr", "reference_kb.json")   # committed corpus

_IALA_URL = "https://www.iala-aism.org/product/r1001-maritime-buoyage-system-mbs/"
_SHOM_TIDE = ("https://refmar.shom.fr/sites/default/files/2025-01/"
              "GT-TSH_CatD_Fiche_Prediction_maree.pdf")
_SHOM_MAREE = "https://maree.shom.fr/"

# (theme, source_id, ref, title, url, text). The `text` is our concise factual
# statement (facts are not copyrightable); each is verified against the cited
# source. IALA Region A (R1001 Ed.2.0 Tables 1–9); SHOM tides (fiche + maree.shom).
REFERENCE: list[tuple] = [
    # ===================== IALA — balisage maritime région A ================
    ("balisage", "iala_a", "IALA R1001 §2.1.3 — marque latérale bâbord (région A)",
     "Marque latérale de bâbord (région A)", _IALA_URL,
     "En venant du large (région A), la marque latérale de bâbord est ROUGE, de "
     "forme cylindrique (« boîte »), pilier ou espar ; voyant éventuel : un "
     "cylindre rouge ; feu rouge (rythme quelconque, sauf 2+1). On la laisse sur "
     "bâbord (à gauche) en entrant."),
    ("balisage", "iala_a", "IALA R1001 §2.1.3 — marque latérale tribord (région A)",
     "Marque latérale de tribord (région A)", _IALA_URL,
     "En région A, la marque latérale de tribord est VERTE, de forme conique, "
     "pilier ou espar ; voyant éventuel : un cône vert pointe vers le haut ; feu "
     "vert. On la laisse sur tribord (à droite) en entrant. (Région B : couleurs "
     "inversées.)"),
    ("balisage", "iala_a", "IALA R1001 §2.1.5 — marques de chenal préféré (région A)",
     "Marques de chenal préféré (région A)", _IALA_URL,
     "Au point où un chenal se divise : chenal préféré à tribord = marque rouge à "
     "une large bande horizontale verte (voyant cylindre rouge) ; chenal préféré à "
     "bâbord = marque verte à large bande rouge (voyant cône vert). Feu à éclats "
     "groupés composés (2+1)."),
    ("balisage", "iala_a", "IALA R1001 §2.2.4 — marque cardinale Nord",
     "Marque cardinale Nord", _IALA_URL,
     "Voyant : deux cônes noirs superposés, pointes vers le HAUT ; corps noir "
     "au-dessus, jaune en dessous ; feu blanc scintillant (VQ) ou rapide (Q). Les "
     "eaux saines sont au nord : on passe au NORD de la marque."),
    ("balisage", "iala_a", "IALA R1001 §2.2.4 — marque cardinale Est",
     "Marque cardinale Est", _IALA_URL,
     "Voyant : deux cônes noirs base à base ; corps noir à une large bande "
     "horizontale jaune ; feu blanc VQ(3) toutes les 5 s ou Q(3) toutes les 10 s. "
     "On passe à l'EST de la marque."),
    ("balisage", "iala_a", "IALA R1001 §2.2.4 — marque cardinale Sud",
     "Marque cardinale Sud", _IALA_URL,
     "Voyant : deux cônes noirs pointes vers le BAS ; corps jaune au-dessus, noir "
     "en dessous ; feu blanc VQ(6) + un éclat long toutes les 10 s, ou Q(6) + un "
     "éclat long toutes les 15 s. On passe au SUD de la marque."),
    ("balisage", "iala_a", "IALA R1001 §2.2.4 — marque cardinale Ouest",
     "Marque cardinale Ouest", _IALA_URL,
     "Voyant : deux cônes noirs pointe à pointe ; corps jaune à une large bande "
     "horizontale noire ; feu blanc VQ(9) toutes les 10 s ou Q(9) toutes les 15 s. "
     "On passe à l'OUEST de la marque."),
    ("balisage", "iala_a", "IALA R1001 §2.3 — marque de danger isolé",
     "Marque de danger isolé", _IALA_URL,
     "Corps noir à une ou plusieurs larges bandes rouges horizontales ; voyant : "
     "deux sphères noires superposées ; feu blanc à éclats groupés (2). Elle est "
     "mouillée SUR (ou au-dessus d')un danger isolé entouré d'eaux saines."),
    ("balisage", "iala_a", "IALA R1001 §2.4 — marque d'eaux saines",
     "Marque d'eaux saines", _IALA_URL,
     "Bandes verticales rouges et blanches ; voyant : une sphère rouge ; feu blanc "
     "isophase, à occultations, un éclat long toutes les 10 s, ou Morse « A ». "
     "Indique des eaux saines tout autour (milieu de chenal, atterrissage) : on "
     "peut la contourner des deux côtés."),
    ("balisage", "iala_a", "IALA R1001 §2.5 — marque spéciale",
     "Marque spéciale", _IALA_URL,
     "Entièrement JAUNE ; voyant éventuel : une croix de Saint-André jaune "
     "(« X ») ; feu jaune (rythme autre que ceux réservés aux cardinales, danger "
     "isolé, eaux saines). Délimite une zone ou un dispositif particulier (ODAS, "
     "zone réglementée, conduite, zone de mouillage…), pas un danger en soi."),

    # ===================== SHOM — marées et cartes ==========================
    ("meteo_maree", "shom", "SHOM — zéro hydrographique (ZH)",
     "Zéro hydrographique (zéro des cartes)", _SHOM_TIDE,
     "Le zéro hydrographique est le niveau de référence commun aux cartes marines "
     "et aux annuaires des marées. En France il est choisi au voisinage des plus "
     "basses mers astronomiques (PBMA), sous lequel la mer ne descend que très "
     "exceptionnellement ; les sondes des cartes y sont rapportées (la profondeur "
     "réelle est donc en général supérieure à la sonde)."),
    ("meteo_maree", "shom", "SHOM — marnage",
     "Marnage", _SHOM_TIDE,
     "Le marnage est la différence de hauteur d'eau entre une pleine mer et la "
     "basse mer consécutive. Marnage < 2 m : microtidal ; 2 à 4 m : mésotidal ; "
     "> 4 m : macrotidal."),
    ("meteo_maree", "shom", "SHOM — coefficient de marée",
     "Coefficient de marée", _SHOM_TIDE,
     "Le coefficient de marée caractérise l'amplitude de la marée (notion utilisée "
     "en France). Les valeurs admises vont de 20 (morte-eau extrême) à 120 "
     "(vive-eau extrême) ; 45 = morte-eau moyenne, 95 = vive-eau moyenne ; le "
     "coefficient 100 correspond au marnage moyen des vives-eaux d'équinoxe. Il est "
     "calculé pour Brest et appliqué à toutes les côtes de France métropolitaine."),
    ("meteo_maree", "shom", "SHOM — vives-eaux et mortes-eaux",
     "Vives-eaux et mortes-eaux", _SHOM_TIDE,
     "En syzygie (pleine ou nouvelle lune, Terre-Lune-Soleil alignés) les ondes "
     "s'additionnent : ce sont les vives-eaux (grand marnage). En quadrature "
     "(premier/dernier quartier) elles s'opposent : ce sont les mortes-eaux "
     "(faible marnage)."),
    ("meteo_maree", "shom", "SHOM — flot et jusant",
     "Flot et jusant", _SHOM_TIDE,
     "Le flot est la marée montante (le niveau monte vers la pleine mer) ; le "
     "jusant est la marée descendante (le niveau baisse vers la basse mer)."),
    ("meteo_maree", "shom", "SHOM — marée semi-diurne et cycle",
     "Marée semi-diurne (Manche / Atlantique)", _SHOM_TIDE,
     "Sur les côtes de la Manche et de l'Atlantique, la marée est de type "
     "semi-diurne : deux pleines mers et deux basses mers par jour. Le cycle de "
     "marée dure environ 12 h 25 (le jour lunaire dure 24 h 50)."),
    ("meteo_maree", "shom", "SHOM — niveaux caractéristiques de la marée",
     "Niveaux caractéristiques (PHMA, PBMA, PMVE…)", _SHOM_TIDE,
     "Niveaux rapportés au zéro hydrographique : PHMA/PBMA = plus hautes/basses "
     "mers astronomiques (marée de coefficient 120) ; PMVE/BMVE = pleines/basses "
     "mers de vive-eau moyenne (coef. 95) ; PMME/BMME = de morte-eau moyenne "
     "(coef. 45). Le niveau moyen est la position moyenne de la surface de la mer."),
    ("meteo_maree", "shom", "Règle des douzièmes (méthode de l'annuaire des marées)",
     "Règle des douzièmes", _SHOM_MAREE,
     "Méthode d'estimation de la hauteur d'eau heure par heure entre la basse mer "
     "et la pleine mer : le marnage monte (ou descend) de 1/12, 2/12, 3/12, 3/12, "
     "2/12, 1/12 par heure successive."),
    ("meteo_maree", "shom", "SHOM — étale",
     "Étale (de niveau / de courant)", _SHOM_MAREE,
     "L'étale est le court moment, à la pleine ou à la basse mer, où le niveau de "
     "l'eau ne varie plus (étale de niveau). La renverse du courant de marée "
     "(étale de courant) est un phénomène voisin mais distinct, qui ne coïncide "
     "pas nécessairement avec l'étale de niveau."),
]


def build_units() -> list[KnowledgeUnit]:
    today = _dt.date.today().isoformat()
    units = []
    for theme, src_id, ref, title, url, text in REFERENCE:
        src = sources_fr.get(src_id)
        units.append(KnowledgeUnit(
            id=make_id(src_id, ref), theme=theme, kind="reference", ref=ref,
            title=title, text=" ".join(text.split()),
            source_id=src_id, source_name=src.name, source_url=url or src.url,
            retrieved=today, legal_version="", licence=src.licence, lang="fr"))
    return units


def build() -> dict:
    units = build_units()
    # Committed corpus (reference facts only — kept separate from the LEGI law).
    with open(REF_JSON, "w", encoding="utf-8") as fh:
        json.dump({"meta": {"country": "FR", "source": "reference",
                            "note": "facts verified against IALA R1001 / SHOM"},
                   "units": [asdict(u) for u in units]}, fh,
                  ensure_ascii=False, indent=2)
    # Also populate the France KB (coexists with the LEGI units by source_id).
    conn = connect(KB_DB)
    conn.execute("DELETE FROM units WHERE source_id IN ('iala_a','shom')")
    write_units(conn, units)
    set_meta(conn, kb_version=_dt.date.today().isoformat(), country="FR")
    conn.close()
    by_src: dict[str, int] = {}
    for u in units:
        by_src[u.source_id] = by_src.get(u.source_id, 0) + 1
    return {"units": len(units), "by_source": by_src}


if __name__ == "__main__":
    s = build()
    print(f"✓ reference corpus built: {REF_JSON}  ({s['units']} facts)")
    print(f"  by source: {s['by_source']}  (+ merged into {KB_DB})")
