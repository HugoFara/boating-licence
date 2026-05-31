"""Hand-authored, sourced "why" concept cards (roadmap group A).

A concept explains the *generative logic* behind a principle so a value or rule
becomes reconstructable instead of memorised. Like the France question seeds
(`seed_fr.py`), these are hand-authored, fully cited, and ship as ``approved`` —
the source is the authority (memory/source-questions-never-recall): every fact in
a body is reproduced from reviewed, already-shipped questions and their primary
source, never invented.

Scoping matters: IALA Region A buoyage is *maritime* (French coastal waters);
Swiss inland (ONI/RNL) and CEVNI rivers use different marks, so a maritime
buoyage concept is loaded ONLY into the banks where it is correct. Each entry
lists the bank ids it ``applies`` to; the build loader writes only those.
"""

from __future__ import annotations

from .schema import Concept

# Each seed: one principle, the bank ids it applies to, shared provenance, and a
# per-language {title, body}. Bodies use blank-line paragraphs (the player splits
# them). Keep them faithful to the cited source.
_SEED: list[dict] = [
    {
        "principle": "iala-buoyage",
        "kind": "principle",
        # French coastal (maritime, IALA Region A). NOT the inland eaux_interieures
        # bank (CEVNI) nor Swiss lakes — those use different buoyage.
        "applies": {"fr_cotiere"},
        "prov": {
            "ref": "Balisage IALA région A — marques latérales, eaux saines, "
                   "marques spéciales",
            "source": "IALA — Système de balisage maritime, région A "
                      "(Recommandation R1001)",
            "url": None, "as_of": None, "licence": None,
        },
        "lang": {
            "fr": {
                "title": "Balisage IALA région A : reconstituer une marque, pas la mémoriser",
                "body": (
                    "En région A (Europe, dont la France), le balisage code le côté "
                    "du chenal par la COULEUR et la FORME — de sorte qu'on peut "
                    "retrouver le sens de n'importe quelle marque au lieu d'en "
                    "apprendre la liste par cœur.\n\n"
                    "Le sens de référence est « en venant du large » (de la mer vers "
                    "le port) :\n"
                    "— Bâbord : marque ROUGE, forme CYLINDRIQUE (« boîte ») ; on la "
                    "laisse sur sa gauche en entrant.\n"
                    "— Tribord : marque VERTE, forme CONIQUE ; on la laisse sur sa "
                    "droite en entrant.\n"
                    "La forme répète l'information du côté : même à contre-jour ou de "
                    "nuit, un cône reste « tribord » et un cylindre « bâbord ».\n\n"
                    "Les autres marques ne bordent pas un chenal, elles qualifient un "
                    "point :\n"
                    "— Eaux saines (milieu de chenal / atterrissage) : bandes "
                    "VERTICALES rouges et blanches, voyant sphérique rouge — pas de "
                    "danger, on passe de chaque côté.\n"
                    "— Marque spéciale : entièrement JAUNE (croix de Saint-André "
                    "jaune) — signale une zone ou un dispositif (baignade, conduite "
                    "immergée, zone réglementée), pas un danger en soi.\n\n"
                    "La règle pratique tient en une phrase : la couleur et la forme "
                    "d'une marque latérale disent de quel côté passer — à condition "
                    "de savoir d'où l'on « vient du large »."
                ),
            },
            "en": {
                "title": "IALA Region A buoyage: reconstruct a mark instead of memorising it",
                "body": (
                    "In Region A (Europe, incl. France), buoyage encodes the side of "
                    "the channel through COLOUR and SHAPE — so you can work out any "
                    "mark rather than learning a list by heart.\n\n"
                    "The reference direction is \"coming from seaward\" (from the sea "
                    "towards the harbour):\n"
                    "— Port hand: RED mark, CYLINDRICAL (can) shape; leave it on your "
                    "left when entering.\n"
                    "— Starboard hand: GREEN mark, CONICAL shape; leave it on your "
                    "right when entering.\n"
                    "The shape repeats the side: even against the light or at night, "
                    "a cone is still \"starboard\" and a can \"port\".\n\n"
                    "Other marks don't edge a channel — they qualify a point:\n"
                    "— Safe water (mid-channel / landfall): VERTICAL red and white "
                    "stripes, red spherical topmark — no danger, pass either side.\n"
                    "— Special mark: all YELLOW (yellow St Andrew's cross) — marks a "
                    "zone or installation (bathing, submerged pipe, restricted area), "
                    "not a danger in itself.\n\n"
                    "The practical rule fits in one sentence: a lateral mark's colour "
                    "and shape tell you which side to pass — once you know which way "
                    "is \"from seaward\"."
                ),
            },
        },
    },
]


def concepts_for(bank_id: str, langs) -> list[Concept]:
    """Return the approved Concept objects to load into one bank.

    ``bank_id`` is the country/option bank key (e.g. "fr_cotiere", "ch", "de",
    "int"); only seeds that list it in ``applies`` are returned, in the requested
    languages. Empty list when nothing applies — the build then ships no concept
    file for that bank, and the player simply shows no card (graceful).
    """
    out: list[Concept] = []
    for e in _SEED:
        if bank_id not in e["applies"]:
            continue
        for lg in langs:
            loc = e["lang"].get(lg)
            if not loc:
                continue
            p = e["prov"]
            out.append(Concept(
                id=f"{e['principle']}.{lg}", principle=e["principle"],
                kind=e["kind"], title=loc["title"], body=loc["body"], lang=lg,
                prov_ref=p["ref"], prov_source=p["source"], prov_url=p["url"],
                prov_as_of=p["as_of"], prov_licence=p["licence"],
                review_status="approved"))
    return out
