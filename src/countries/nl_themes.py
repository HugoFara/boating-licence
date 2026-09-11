"""Dutch exam-theme taxonomy + tagger (Klein Vaarbewijs I / II).

Two official documents define this taxonomy between them, and nothing here is
invented:

* **What the exam covers** — *Binnenvaartregeling* art. 7.15 lists the subjects
  of the klein-vaarbewijs exam by law. Lid 1 (KVB I): the legal provisions
  relevant to safe navigation on rivers, canals and lakes; handling the
  propulsion machinery; safety measures; the waterways, the state of the fairway
  and elementary meteorology; and navigating, manoeuvring and what to do in
  special circumstances. Lid 2 (KVB II) adds: the legal provisions for the
  Westerschelde, the Eems and the Dollard; the use of nautical publications;
  course and position fixing; and meteorology.
* **How the legal provisions are organised** — the *Binnenvaartpolitiereglement*
  (BPR) splits them into chapters, and chapter 3 (optische tekens), 4
  (geluidsseinen), 5 (verkeerstekens) and 6 (vaarregels) are exactly the four
  blocks a learner studies. So the "wettelijke bepalingen" subject is realised
  here as one theme per BPR chapter rather than as a single opaque bucket.

That split is what makes the tagger **deterministic** for the ingested law: a
Dutch article number is always chapter-qualified ("Artikel 5.01" is in chapter 5,
with no exception anywhere in the BPR), so the chapter — hence the theme — is
read straight off the ref. Annexes map by their own number. Keyword rules are the
fallback for the acts outside the BPR (the Binnenvaartwet/-besluit/-regeling
licensing spine) and for anything reaching the tagger without a parseable ref.

Labels are Dutch: the exam is Dutch, its sources are Dutch-only (Dutch law is
enacted in one language), and the German bank sets the precedent that a national
bank speaks its own language.
"""

from __future__ import annotations

import re

# Canonical theme ids (stable keys) -> human label (Dutch, as on the exam).
THEMES: dict[str, str] = {
    # --- "wettelijke bepalingen", realised as the BPR's own chapter split -----
    "algemene_bepalingen": "Algemene bepalingen en kentekens",
    "optische_tekens": "Optische tekens van schepen (lichten en dagmerken)",
    "geluidsseinen": "Geluidsseinen",
    "marifoon_radar": "Marifoon, radar en Inland AIS",
    "verkeerstekens": "Verkeerstekens",
    "betonning": "Markering van het vaarwater (betonning)",
    "vaarregels": "Vaarregels",
    "ligplaats": "Ligplaats nemen",
    "bijzondere_vaarwegen": "Bijzondere bepalingen per vaarweg",
    "vaarbewijs": "Vaarbewijs, registratie en handhaving",
    # --- the non-BPR exam subjects (art. 7.15) --------------------------------
    "voortstuwing": "Behandeling van de voortstuwingswerktuigen",
    "veiligheid": "Veiligheidsmaatregelen",
    "vaarwater": "Waterwegen en omstandigheden van het vaarwater",
    "manoeuvreren": "Varen, manoeuvreren en bijzondere omstandigheden",
    "milieu": "Milieu en afvalstoffen",
    # --- KVB II only ----------------------------------------------------------
    "navigatie": "Nautische bescheiden, koers- en plaatsbepaling",
    # id deliberately not "meteorologie": that key is already the Swiss theme,
    # and theme ids are a single global namespace (see tests/test_countries.py).
    "weerkunde": "Meteorologie",
}

# Themes no ingested *law* source grounds — they are seamanship and craft
# subjects the statute names (art. 7.15) but no ordinance spells out. Scaffolded
# so a law-only Dutch build stays clean (see normalize's missing-theme check).
EXTENSION_THEMES: frozenset[str] = frozenset(
    {"voortstuwing", "vaarwater", "manoeuvreren", "navigatie", "weerkunde"})

# --- the official test matrices (CBR toetsmatrijs) ------------------------------
# The CBR examendocument per exam (hoofdstuk 3, "Toetsmatrijs", ingangsdatum
# 1 januari 2020; read 2026-09-11 from
#   https://www.cbr.nl/nl/service/nl/artikel/examendocument-kvb1  (21 pp.)
#   https://www.cbr.nl/nl/service/nl/artikel/examendocument-kvb2  (17 pp.))
# prints one row per toetsterm: its question number(s), count and points. That is
# the exact weighting of the paper — KVB1: 40 questions, 80 points, cesuur 56
# (A wettelijke bepalingen 18 q/35 pt · B techniek/veiligheid 5/12 · C vaarwater/
# weer 9/16 · D varen/manoeuvreren 8/17); KVB2: 27 questions, 50 points, cesuur 35
# (E wettelijke bepalingen ruime wateren 8/13 · F navigatie 19/37).
#
# Each row is mapped to a theme of this taxonomy by the same rule the tagger
# uses — a BPR toetsterm names its chapter, and _CHAPTER_THEME decides (so
# "snelle motorboten, Hfdst. 8" is a steering-rules slot and "kleine schepen,
# Hfdst. 9" a per-waterway one, exactly as the ingested articles are filed).
# Non-BPR rows follow the subject the programme puts them under: KVB1's
# "elementaire meteorologie" sits inside subject C (vaarwater) by art. 7.15 lid 1,
# whereas KVB2's meteorologie is its own subject (weerkunde); the SRW rows of
# KVB2 are the Westerschelde regime — per-waterway provisions. Labels are the
# matrix's own wording, abridged.
TOETSMATRIJS: dict[str, tuple[tuple[str, str, str, int], ...]] = {
    "KVB-1": (
        ("A.1", "Scheepvaartverkeerswet, Binnenvaartwet, Binnenvaartbesluit, Wetboek van Koophandel", "vaarbewijs", 1),
        ("A.3", "Toepassingsgebied alle scheepvaartreglementen; Vaststellingsbesluit BPR; BPR op RPR-gebied", "algemene_bepalingen", 1),
        ("A.4", "BPR definities en algemene bepalingen, Hfdst. 1 en 2", "algemene_bepalingen", 1),
        ("A.6", "BPR navigatielichten, Hfdst. 3", "optische_tekens", 2),
        ("A.7", "BPR dagtekens, Hfdst. 3", "optische_tekens", 2),
        ("A.8", "BPR geluidsseinen, Hfdst. 4, bijlage 6", "geluidsseinen", 1),
        ("A.9", "BPR marifoon inrichting en gebruik, Hfdst. 4, bijlage 9", "marifoon_radar", 2),
        ("A.11", "BPR vaarregels, art. 1.04, 1.05 en 6.01 t/m 6.05", "vaarregels", 3),
        ("A.12", "BPR vaarregels, art. 6.07 t/m 6.11", "vaarregels", 3),
        ("A.13", "BPR vaarregels, art. 6.12 t/m 6.16", "vaarregels", 3),
        ("A.14", "BPR vaarregels, art. 6.17 t/m 6.23", "vaarregels", 3),
        ("A.15", "BPR bruggen, sluizen, art. 6.24 – 6.28", "vaarregels", 2),
        ("A.16", "BPR slecht zicht, art. 6.29 – 6.33", "vaarregels", 2),
        ("A.17", "BPR stilliggen, Hfdst. 7", "ligplaats", 2),
        ("A.18", "BPR snelle motorboten, Hfdst. 8", "vaarregels", 2),
        ("A.19", "BPR kleine schepen, Hfdst. 9", "bijzondere_vaarwegen", 1),
        ("A.20", "RPR definities en algemene bepalingen, dagtekens en verlichting", "algemene_bepalingen", 1),
        ("A.21", "RPR vaarregels", "vaarregels", 3),
        ("B.1", "Accu's en elektriciteit, motorkennis, oliedruk en koelwater", "voortstuwing", 2),
        ("B.4", "Brandpreventie en brandbestrijding", "veiligheid", 3),
        ("B.5", "Reddingsmiddelen", "veiligheid", 2),
        ("B.7", "Veiligheidsmiddelen (gas)", "veiligheid", 3),
        ("B.8", "Veiligheidsmiddelen (overig)", "veiligheid", 2),
        ("C.1", "Betonning", "betonning", 2),
        ("C.2", "Oeververlichting en lichtkarakters", "betonning", 2),
        ("C.3", "Aflezen hoogteschalen (brug)", "vaarwater", 1),
        ("C.4", "Aflezen peilschalen (waterpeil)", "vaarwater", 1),
        ("C.5", "Berekenen vaarwegdiepte en brughoogte", "vaarwater", 3),
        ("C.6", "Meteorologie termen", "vaarwater", 1),
        ("C.7", "Meteorologie druksystemen", "vaarwater", 2),
        ("C.8", "Tekens langs de vaarweg, verboden en geboden", "verkeerstekens", 2),
        ("C.9", "Tekens langs de vaarweg, andere dan verboden en geboden", "verkeerstekens", 2),
        ("D.1", "Schroef- en roerwerking", "manoeuvreren", 2),
        ("D.3", "Ankeren", "manoeuvreren", 2),
        ("D.4", "Zuiging en golfslag, ontmoeten en voorbijlopen", "manoeuvreren", 2),
        ("D.5", "Schutten en dode hoek", "manoeuvreren", 2),
        ("D.6", "Slepen, man-overboord en bijzondere omstandigheden", "manoeuvreren", 2),
        ("D.7", "Zonder boegschroef aankomen, wegvaren, keren zonder wind/stroom", "manoeuvreren", 2),
        ("D.8", "Zonder boegschroef aankomen, wegvaren, keren met wind/stroom", "manoeuvreren", 2),
        ("D.9", "Met boegschroef aankomen, wegvaren, keren met of zonder wind/stroom", "manoeuvreren", 3),
    ),
    "KVB-2": (
        ("E.1", "Toepassingsgebied SRW en SRE/BVA en aangrenzend BPR- en SRKGT-gebied", "bijzondere_vaarwegen", 1),
        ("E.2", "SRW definities en verantwoordelijkheden (art. 2, 3)", "bijzondere_vaarwegen", 1),
        ("E.3", "SRW algemene bepalingen (art. 4, 6, 7), redegebied, diverse art.", "bijzondere_vaarwegen", 1),
        ("E.4", "SRW uitwijkbepalingen (art. 9 t/m 19)", "bijzondere_vaarwegen", 2),
        ("E.5", "SRW lichten, dagmerken, geluidsseinen (art. 23 t/m 31, 35, 37)", "bijzondere_vaarwegen", 2),
        ("E.7", "SRW lichten, dagmerken, kleine schepen (art. 41)", "bijzondere_vaarwegen", 2),
        ("E.8", "SRW vaarregels kleine schepen (art. 9 t/m 19 en 42)", "bijzondere_vaarwegen", 2),
        ("E.12", "BPR vaarregels op de Waddenzee, IJsselmeer, Markermeer, IJmeer en Oosterschelde (art. 6.16, 6.17)", "vaarregels", 2),
        ("F.1", "Meteorologie, termen en druksystemen", "weerkunde", 2),
        ("F.2", "Meteorologie, fronten", "weerkunde", 2),
        ("F.3", "Bronnen voor veilige vaart (kaart, stroomatlas, gids, BaZ)", "navigatie", 1),
        ("F.4a", "Kaartlezen, kaarttekens (I)", "navigatie", 1),
        ("F.4b", "Kaartlezen, kaarttekens (II)", "navigatie", 1),
        ("F.5", "Betonning, cardinaal", "betonning", 1),
        ("F.6", "Betonning overig", "betonning", 1),
        ("F.7a", "Getij algemeen (I)", "navigatie", 2),
        ("F.7b", "Getij algemeen (II)", "navigatie", 2),
        ("F.9", "Getij verticaal, berekeningen", "navigatie", 2),
        ("F.10", "Koersbepaling algemeen", "navigatie", 1),
        ("F.11", "Koersbepaling berekeningen I (KK > WK en WK > KK)", "navigatie", 2),
        ("F.12", "Koersbepaling berekeningen II (met drift)", "navigatie", 3),
        ("F.13", "Koersbepaling berekeningen III (met stroom, eventueel drift)", "navigatie", 3),
        ("F.22", "GPS", "navigatie", 1),
        ("F.24", "Kaartpassen Markermeer — positie, koers, afstand, drift (deel I)", "navigatie", 4),
        ("F.25", "Kaartpassen Markermeer — deel II", "navigatie", 2),
        ("F.26", "Kaartpassen Waddenzee — positie, koers, afstand, drift (deel I)", "navigatie", 4),
        ("F.27", "Kaartpassen Waddenzee — deel II", "navigatie", 2),
    ),
}
TOETSMATRIJS_SOURCE = "CBR — Examendocument Klein Vaarbewijs 1 / 2, toetsmatrijs (ingangsdatum 1 januari 2020)"
TOETSMATRIJS_AS_OF = "2026-09-11"


# Which themes each permit's exam draws on (Binnenvaartregeling art. 7.15).
_KVB1 = ("algemene_bepalingen", "optische_tekens", "geluidsseinen",
         "marifoon_radar", "verkeerstekens", "betonning", "vaarregels",
         "ligplaats", "bijzondere_vaarwegen", "vaarbewijs", "voortstuwing",
         "veiligheid", "vaarwater", "manoeuvreren", "milieu")
# Lid 2 is explicitly cumulative — "de in het eerste lid genoemde onderwerpen
# alsmede …" — so KVB II is KVB I plus navigation and meteorology.
_KVB2 = _KVB1 + ("navigatie", "weerkunde")

PERMIT_THEMES: dict[str, tuple[str, ...]] = {
    "KVB-1": _KVB1,
    "KVB-2": _KVB2,
}

# --- deterministic mapping for the ingested law -------------------------------
# BPR chapter -> theme. Chapters 8-13 are the per-waterway special provisions.
_CHAPTER_THEME: dict[str, str] = {
    "1": "algemene_bepalingen", "2": "algemene_bepalingen",
    "3": "optische_tekens",
    "4": "geluidsseinen", "4A": "marifoon_radar",
    "5": "verkeerstekens",
    "6": "vaarregels",
    "7": "ligplaats",
    # Chapter 8 ("Aanvullende bepalingen") is not per-waterway at all: it is the
    # conduct code for fast motorboats, waterskiing and swimming, which the
    # ministerial exam programme lists beside the steering rules. Filing it as a
    # per-waterway provision would tell a learner that a waterskiing rule belongs
    # to a stretch of river.
    "8": "vaarregels",
    "9": "bijzondere_vaarwegen",
    "10": "bijzondere_vaarwegen", "11": "bijzondere_vaarwegen",
    "12": "bijzondere_vaarwegen", "13": "bijzondere_vaarwegen",
}

# Annexes that carry the SAME subject in both police reglementen — checked
# against each act's own annex titles, not assumed: 1 (home-port letters), 3
# (optische tekens), 6 (geluidsseinen), 7 (verkeerstekens), 8 (markering van het
# vaarwater = the IALA-A buoyage annex) and 13 (scheepsbescheiden).
_ANNEX_THEME: dict[str, str] = {
    "1": "algemene_bepalingen", "3": "optische_tekens", "6": "geluidsseinen",
    "7": "verkeerstekens", "8": "betonning", "13": "algemene_bepalingen",
}

# The rest of the numbering diverges between the two — BPR bijlage 11 is a list of
# waterways, RPR bijlage 11 is the Inland AIS data set — so these apply only to
# the BPR. Bijlage 10, 11 and 14-18 list the waterways a chapter-9/10 rule covers.
_ANNEX_THEME_BPR: dict[str, str] = {
    "4": "marifoon_radar", "9": "marifoon_radar", "12": "veiligheid",
    "10": "bijzondere_vaarwegen", "11": "bijzondere_vaarwegen",
    "14": "bijzondere_vaarwegen", "15": "bijzondere_vaarwegen",
    "16": "bijzondere_vaarwegen", "17": "bijzondere_vaarwegen",
    "18": "bijzondere_vaarwegen",
}

# The chapter/annex mapping is a fact about the two police reglementen (their
# chapters 1-7 are subject-for-subject identical), NOT about Dutch law at large:
# "Artikel 7.15" of the Binnenvaartregeling is an exam rule, not a berthing rule.
_POLITIEREGLEMENT = re.compile(r"politiereglement", re.I)
_BPR = re.compile(r"binnenvaartpolitiereglement", re.I)

_RADIO_TITLE = re.compile(r"\b(marifoon|radar|AIS|ECDIS)\b", re.I)
_BUOYAGE_TITLE = re.compile(r"markering van (?:het vaarwater|de vaarweg)", re.I)

_ARTICLE_REF = re.compile(r"\bartikel\s+(\d+[A-Z]?)\.\d", re.I)
_ANNEX_REF = re.compile(r"\bbijlage\s+(\d+)", re.I)

# Keyword fallback, ordered most-specific first. Used for the licensing acts
# (Binnenvaartwet/-besluit/-regeling) and any unit without a parseable ref.
_KEYWORDS: tuple[tuple[str, re.Pattern[str]], ...] = (
    # A definitions article, whatever act it sits in. First, because its own
    # vocabulary is every other theme's vocabulary: the Binnenvaartbesluit's
    # definition list mentions a bunker station's "permanente ligplaats" and was
    # filed as a berthing rule.
    ("algemene_bepalingen", re.compile(
        r"wordt,?(?:\s*tenzij anders is bepaald,)?\s*verstaan onder", re.I)),
    ("vaarbewijs", re.compile(
        r"\b(vaarbewijs|vaarbewijzen|kwalificatiecertificaat|dienstboekje|"
        r"examen|geneeskundige verklaring|gezondheidsverklaring|"
        r"ongeldigverklaring|vaarbevoegdheid|register)\b", re.I)),
    ("marifoon_radar", re.compile(r"\b(marifoon|marifonie|radar|AIS)\b", re.I)),
    ("geluidsseinen", re.compile(
        r"\b(geluidssein\w*|geluidsein\w*|scheepsklok|stoot|lange stoot|"
        r"korte stoot|mistsein\w*)\b", re.I)),
    ("optische_tekens", re.compile(
        r"\b(licht(en|voering)?|toplicht|boordlicht\w*|heklicht|rondom schijnend|"
        r"dagmerk\w*|bol|kegel|cilinder|ruit)\b", re.I)),
    # NOT a bare "ton": in Dutch that is also the tonnage unit, and it filed the
    # Binnenvaartwet's zone article and a 50-tonne haulage threshold under buoyage.
    ("betonning", re.compile(
        r"\b(betonning|bebakening|markering van (?:het vaarwater|de vaarweg)|"
        r"boei\w*|spitse ton\w*|stompe ton\w*|kardinale|lichtenlijn\w*)\b", re.I)),
    ("verkeerstekens", re.compile(
        r"\b(verkeersteken\w*|verbodsteken\w*|gebodsteken\w*|"
        r"beperkingsteken\w*|aanwijzingsteken\w*|bord)\b", re.I)),
    ("vaarregels", re.compile(
        r"\b(voorrang|uitwijk\w*|koers\w* houden|oplopen|voorbijlopen|"
        r"tegengestelde koersen|stuurboord|bakboord|vaarregel\w*)\b", re.I)),
    ("ligplaats", re.compile(r"\b(ligplaats|ankeren|meren|afmeren)\b", re.I)),
    ("milieu", re.compile(
        r"\b(afvalstof\w*|olie|verontreinig\w*|milieu|bilgewater)\b", re.I)),
    ("veiligheid", re.compile(
        r"\b(gevaarlijke stoffen|reddingsmiddel\w*|reddingsvest|brandblus\w*|"
        r"veiligheid\w*)\b", re.I)),
)


def tag_theme(ref: str = "", title: str = "", text: str = "",
              default: str | None = None) -> str:
    """Return the Dutch theme id for a knowledge unit.

    Deterministic for the BPR (chapter from the article number, or the annex
    number); keyword-scanned otherwise; ``default`` last.
    """
    haystack_ref = f"{ref} {title}"
    if _POLITIEREGLEMENT.search(ref or ""):
        m = _ANNEX_REF.search(haystack_ref)
        if m:
            annexes = dict(_ANNEX_THEME)
            if _BPR.search(ref or ""):
                annexes.update(_ANNEX_THEME_BPR)
            if m.group(1) in annexes:
                return annexes[m.group(1)]
        m = _ARTICLE_REF.search(haystack_ref)
        if m and m.group(1).upper() in _CHAPTER_THEME:
            theme = _CHAPTER_THEME[m.group(1).upper()]
            # The BPR splits sound (ch. 4) from radio and radar (ch. 4A); the RPR
            # combines them in one chapter 4. Where the act itself titles the
            # article "Marifoon" or "Radar", that heading wins over the chapter.
            if theme == "geluidsseinen" and _RADIO_TITLE.search(title or ""):
                return "marifoon_radar"
            # Likewise RPR 5.02 is titled "Verkeerstekens ter markering van de
            # vaarweg" — a buoyage rule sitting in the signs chapter.
            if theme == "verkeerstekens" and _BUOYAGE_TITLE.search(title or ""):
                return "betonning"
            return theme

    haystack = " ".join((ref, title, text))
    for theme_id, pattern in _KEYWORDS:
        if pattern.search(haystack):
            return theme_id
    if default and default in THEMES:
        return default
    return "algemene_bepalingen"


def is_valid(theme_id: str) -> bool:
    return theme_id in THEMES
