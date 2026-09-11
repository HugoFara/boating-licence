"""The Netherlands — recreational-boating theory exams (Klein Vaarbewijs).

Defined natively against :mod:`countries.base`. Three things make the Netherlands
the strongest remaining target in the project's region:

* **Dutch law carries no copyright at all.** *Auteurswet* art. 11: "Er bestaat
  geen auteursrecht op wetten, besluiten en verordeningen, door de openbare macht
  uitgevaardigd" — no copyright exists on laws, decrees and ordinances issued by
  public authority. That is cleaner than §5(1) UrhG (which is a limitation) and
  cleaner than anything the project has ingested so far.
* **It is machine-readable to a fault.** KOOP publishes every consolidated state
  of every act as structured XML (the Basis Wetten Bestand), each act indexed by a
  manifest naming the state in force. These are the ``kind="bwb"`` sources below.
* **The annex figures come with it.** The BPR alone ships 400+ official PNGs —
  every waterway sign, every light configuration, the buoyage system, the sound
  patterns. Four of those families already have generated diagrams in this repo
  (:mod:`src.questions.diagrams`); here the official plates are in the law itself.

**No official question catalogue.** Unlike Germany's ELWIS, the CBR does not
publish the klein-vaarbewijs bank (only sample exams). So the Dutch question set
must be **law-seeded** — authored from the BPR and the Binnenvaartregeling behind
the review gate — exactly the route already taken for the Bodensee/BSO set. That
is a separate task; this module is the ingestion + exam model it will build on.

Confidence: every legal fact below is read from the act named beside it (verified
2026-08-15). The exam *format* — question counts, weights, pass marks, fees — is
not in any statute; it is CBR's, taken from the CBR's own exam pages and marked
volatile where it drifts.
"""

from __future__ import annotations

from ..sources import Source
from . import nl_examscope, nl_themes
from .base import Country, ExamRules, PathStep, Permit, ReadingRef, Reference, Region

LEGAL_BASIS = (
    "Nederlands recht kent géén auteursrecht op wetgeving: Auteurswet art. 11 — "
    "\"Er bestaat geen auteursrecht op wetten, besluiten en verordeningen, door de "
    "openbare macht uitgevaardigd, noch op rechterlijke uitspraken en "
    "administratieve beslissingen.\" De geconsolideerde teksten en de bijbehorende "
    "bijlage-illustraties worden door KOOP (wetten.overheid.nl) als open data "
    "gepubliceerd en zijn daarmee vrij herbruikbaar. Het CBR publiceert géén "
    "officiële vragenbank voor het klein vaarbewijs — alleen voorbeeldexamens — "
    "dus de Nederlandse vragen worden uit de wet zelf afgeleid (law-seeded, achter "
    "de review gate), nooit uit een commerciële bank overgenomen.")

_BWB_LICENCE = ("Public domain — Dutch law carries no copyright (Auteurswet "
                "art. 11). Consolidated text + annex figures via wetten.overheid.nl "
                "/ KOOP open data.")


# --- Dutch law (kind="bwb": repository.officiele-overheidspublicaties.nl) ------
# The BPR is the Dutch enactment of CEVNI and the spine of the KVB exam; the RPR
# is the Rhine regime (CCNR) that diverges from it on the Rhine/Waal/Lek; the STZ
# is the maritime code for the territorial sea (COLREG-derived). The licensing
# spine (wet/besluit/regeling) is what defines the permits themselves.
SOURCES: list[Source] = [
    Source(
        id="bpr", kind="bwb", lang="nl", bwb_id="BWBR0003628",
        name="Binnenvaartpolitiereglement (BPR)",
        url="https://wetten.overheid.nl/BWBR0003628",
        default_theme="vaarregels", licence=_BWB_LICENCE),
    Source(
        id="rpr", kind="bwb", lang="nl", bwb_id="BWBR0006923",
        name="Rijnvaartpolitiereglement 1995 (RPR)",
        url="https://wetten.overheid.nl/BWBR0006923",
        default_theme="vaarregels", licence=_BWB_LICENCE),
    Source(
        id="stz", kind="bwb", lang="nl", bwb_id="BWBR0007914",
        name="Scheepvaartreglement territoriale zee (STZ)",
        url="https://wetten.overheid.nl/BWBR0007914",
        default_theme="vaarregels", licence=_BWB_LICENCE),
    # Named by the ministerial exam programme (CBR Examendocument KVB1, ch. 1) as
    # the basis of every scheepvaartreglement and the home of the alcohol limit and
    # the withdrawal of a vaarbewijs — but absent from the first ingestion pass.
    Source(
        id="svw", kind="bwb", lang="nl", bwb_id="BWBR0004364",
        name="Scheepvaartverkeerswet (SVW)",
        url="https://wetten.overheid.nl/BWBR0004364",
        default_theme="vaarbewijs", licence=_BWB_LICENCE),
    Source(
        id="vaststellingsbesluit_bpr", kind="bwb", lang="nl", bwb_id="BWBR0003627",
        name="Vaststellingsbesluit Binnenvaartpolitiereglement",
        url="https://wetten.overheid.nl/BWBR0003627",
        default_theme="algemene_bepalingen", licence=_BWB_LICENCE),
    # The exam names exactly one article of the Wetboek van Koophandel — art. 785,
    # the duty to render assistance and to exchange details after a collision. The
    # code has 1307 articles of commercial law, so only that one is ingested.
    Source(
        id="wvk", kind="bwb", lang="nl", bwb_id="BWBR0001838",
        only_refs=("Artikel 785",),
        name="Wetboek van Koophandel",
        url="https://wetten.overheid.nl/BWBR0001838",
        default_theme="veiligheid", licence=_BWB_LICENCE),
    Source(
        id="binnenvaartwet", kind="bwb", lang="nl", bwb_id="BWBR0023009",
        name="Binnenvaartwet",
        url="https://wetten.overheid.nl/BWBR0023009",
        default_theme="vaarbewijs", licence=_BWB_LICENCE),
    Source(
        id="binnenvaartbesluit", kind="bwb", lang="nl", bwb_id="BWBR0025631",
        name="Binnenvaartbesluit",
        url="https://wetten.overheid.nl/BWBR0025631",
        default_theme="vaarbewijs", licence=_BWB_LICENCE),
    Source(
        id="binnenvaartregeling", kind="bwb", lang="nl", bwb_id="BWBR0025958",
        name="Binnenvaartregeling",
        url="https://wetten.overheid.nl/BWBR0025958",
        default_theme="vaarbewijs", licence=_BWB_LICENCE),
]


REFERENCES: tuple[Reference, ...] = (
    Reference(
        name="CBR — voorbeeldexamens Klein Vaarbewijs I en II",
        url="https://www.cbr.nl/nl/service/nl/artikel/voorbeeldexamen-kvb1",
        note="Het CBR publiceert géén officiële vragenbank (anders dan ELWIS in "
             "Duitsland), alleen voorbeeldexamens. Geen hergebruikvrijgave, dus "
             "NIET ingestiet: de Nederlandse vragen worden uit het BPR en de "
             "Binnenvaartregeling afgeleid (law-seeded) en het voorbeeldexamen "
             "wordt hooguit intern als afstemming/divergentiecontrole gebruikt."),
    Reference(
        name="Scheepvaartreglement Westerschelde 1990",
        url="https://wetten.overheid.nl/BWBR0005393",
        note="Nederlands-Belgisch regime op de Westerschelde — eigen reglement dat "
             "van het BPR afwijkt (KVB II-vaargebied). Vrij van auteursrecht "
             "(Auteurswet art. 11); nog niet ingestiet."),
    Reference(
        name="Scheepvaartreglement Eemsmonding",
        url="https://wetten.overheid.nl/BWBR0004552",
        note="Nederlands-Duits regime op de Eems/Dollard (KVB II-vaargebied). Vrij "
             "van auteursrecht; nog niet ingestiet."),
    Reference(
        name="Scheepvaartreglement Gemeenschappelijke Maas",
        url="https://wetten.overheid.nl/BWBR0006618",
        note="Nederlands-Belgisch regime op de Gemeenschappelijke Maas. Vrij van "
             "auteursrecht; nog niet ingestiet."),
)


# --- recreational permits ------------------------------------------------------
# WHEN a klein vaarbewijs is required: Binnenvaartbesluit art. 16 lid 1 — ships
# 15 to <20 m; pleasure craft 15 to <25 m; and any ship under 15 m able to make
# more than 20 km/h through the water. WHICH one: lid 2/3 — "rivieren, kanalen en
# meren" needs KVB I, "de overige binnenwateren" needs KVB II, where lid 4 defines
# the former as every inland water EXCEPT those classified as of maritime nature.
_KVB_REQUIRED = ("Vereist voor schepen van 15 tot 20 m, pleziervaartuigen van "
                 "15 tot 25 m, en elk schip korter dan 15 m dat sneller dan "
                 "20 km/u door het water kan (Binnenvaartbesluit art. 16 lid 1).")

# Binnenvaartregeling art. 7.11b lid 2 — the statutory list, verbatim in scope.
MARITIEME_WATEREN = ("Westerschelde", "Oosterschelde", "Waddenzee", "Eems",
                     "Dollard", "IJsselmeer", "IJmeer",
                     "Markermeer (met uitzondering van de Gouwzee)")

PERMITS: dict[str, Permit] = {
    "KVB-1": Permit(
        code="KVB-1", label="Klein Vaarbewijs I (rivieren, kanalen en meren)",
        themes=nl_themes.PERMIT_THEMES["KVB-1"], drive="motor+sail",
        track="inland",
        # CBR scores by weighted question (1-3 points), not one point each, and
        # passes at 70 % of the total — the same shape as the Swiss VKS paper, so
        # it is modelled as all_or_nothing on points rather than as blocks.
        exam=ExamRules(questions=40, time_limit_min=60, scoring="all_or_nothing",
                       pass_points=56, total_points=80,
                       note="40 meerkeuzevragen in 60 minuten; 1 tot 3 punten per "
                            "vraag, 80 punten totaal, geslaagd vanaf 56 punten "
                            "(70 %). Bron: CBR (examenformat, niet wettelijk "
                            "vastgelegd)."),
        note=_KVB_REQUIRED + " Geldig op alle binnenwateren behalve de wateren "
             "van maritieme aard (Binnenvaartbesluit art. 16 lid 2 en 4)."),
    "KVB-2": Permit(
        code="KVB-2", label="Klein Vaarbewijs II (alle binnenwateren)",
        themes=nl_themes.PERMIT_THEMES["KVB-2"], drive="motor+sail",
        track="inland",
        exam=ExamRules(questions=27, time_limit_min=90, scoring="all_or_nothing",
                       pass_points=35, total_points=50,
                       note="27 vragen (23 meerkeuze + 4 open) in 90 minuten; 1 tot "
                            "4 punten per vraag, 50 punten totaal, geslaagd vanaf "
                            "35 punten (70 %). Komt bovenop KVB I. Bron: CBR."),
        note="Vereist voor de vaart op de overige binnenwateren — de wateren van "
             "maritieme aard: " + ", ".join(MARITIEME_WATEREN) +
             " (Binnenvaartbesluit art. 16 lid 3, Binnenvaartregeling art. 7.11b "
             "lid 2). Het klein vaarbewijs geldt tevens als ICC voor de "
             "binnenvaart (Binnenvaartregeling bijlage 7.3)."),
}


# --- path-to-permit scaffolding ------------------------------------------------
# Authored from the acts and the CBR's own pages (never from memory), verified
# 2026-08-15. Dutch only (this bank ships nl). There is no practical exam for the
# klein vaarbewijs — the theory paper is the whole exam, which is why no
# `practical` step appears here; adding one would invent a requirement.
_WET27 = "https://wetten.overheid.nl/BWBR0023009#Hoofdstuk5_Paragraaf2_Artikel27"
_BESLUIT20 = "https://wetten.overheid.nl/BWBR0025631#Hoofdstuk4_Paragraaf2_Artikel20"
_CBR_KVB1 = ("https://www.cbr.nl/nl/recreatievaart-ppl-rzam/nl-1/"
             "theorie-examen-klein-vaarbewijs-1")
_REGELING73 = "https://wetten.overheid.nl/BWBR0025958#Bijlage7.3"

# --- Where to learn the theory --------------------------------------------------
# Verified 2026-09-11. The CBR publishes, per exam, an *examendocument* holding the
# ministerial examenprogramma, the afbakening and the toetsmatrijs — the exact
# syllabus with points per topic (KVB1: 40 questions / 80 points, cesuur 56;
# A wettelijke bepalingen 35 pt, B techniek/veiligheid 12, C vaarwater/weer 16,
# D varen/manoeuvreren 17). That document is the syllabus (basis "programme").
# The law is free on wetten.overheid.nl (basis "units"). The ANWB course book is
# listed on the strength of its published table of contents (basis "toc": ch. 1
# wetten en reglementen, 2 techniek/veiligheid/milieu, 3 vaarwater/weer, 4 praktijk
# van het varen, further chapters KVB2). "Varen doe je Samen" is the free
# safety-campaign knowledge base of Rijkswaterstaat, provinces, KNRM and the
# Watersportverbond; its themes follow its section list (basis "toc").
_CBR_KVB1 = "https://www.cbr.nl/nl/recreatievaart-ppl-rzam/recreatievaart/theorie-examen-kvb1"
_CBR_KVB2 = "https://www.cbr.nl/nl/recreatievaart-ppl-rzam/recreatievaart/theorie-examen-kvb2"
_CBR_DOC1 = "https://www.cbr.nl/nl/service/nl/artikel/examendocument-kvb1"
_CBR_DOC2 = "https://www.cbr.nl/nl/service/nl/artikel/examendocument-kvb2"
_CBR_SAMPLE1 = "https://www.cbr.nl/nl/service/nl/artikel/voorbeeldexamen-kvb1"
_ANWB = "https://www.anwb.nl/webwinkel/p/140952/anwb-cursusboek-klein-vaarbewijs-i-en-ii"
_VDJS = "https://varendoejesamen.nl/"

READING: tuple[ReadingRef, ...] = (
    ReadingRef(
        code="cbr_examendocument_kvb1", kind="programme",
        title="Examendocument Klein Vaarbewijs 1 — examenprogramma, afbakening en toetsmatrijs",
        publisher="CBR, divisie CCV (programma vastgesteld door de Minister van I&W)",
        url=_CBR_DOC1, lang="nl", cost="free", official=True,
        themes=nl_themes.PERMIT_THEMES["KVB-1"], basis="programme",
        permit_scope=("KVB-1",), source=_CBR_DOC1, as_of="2026-09-11",
        body={"nl": "Het officiële examenprogramma met per onderwerp de te behalen "
                    "punten (40 vragen, 80 punten, geslaagd bij 56): wettelijke "
                    "bepalingen 35, techniek en veiligheid 12, vaarwater en weer 16, "
                    "varen en manoeuvreren 17. Ingangsdatum 1 januari 2020."}),
    ReadingRef(
        code="cbr_examendocument_kvb2", kind="programme",
        title="Examendocument Klein Vaarbewijs 2 — examenprogramma, afbakening en toetsmatrijs",
        publisher="CBR, divisie CCV (programma vastgesteld door de Minister van I&W)",
        url=_CBR_DOC2, lang="nl", cost="free", official=True,
        themes=nl_themes.PERMIT_THEMES["KVB-2"], basis="programme",
        permit_scope=("KVB-2",), source=_CBR_KVB2, as_of="2026-09-11",
        body={"nl": "Het officiële examenprogramma voor het aanvullende examen KVB2 "
                    "(alle binnenwateren): navigatie en weerkunde bovenop de KVB1-stof."}),
    ReadingRef(
        code="cbr_voorbeeldexamen_kvb1", kind="sample_exam",
        title="Voorbeeldexamen Klein Vaarbewijs 1",
        publisher="CBR", url=_CBR_SAMPLE1, lang="nl", cost="free", official=True,
        themes=nl_themes.PERMIT_THEMES["KVB-1"], basis="programme",
        permit_scope=("KVB-1",), source=_CBR_KVB1, as_of="2026-09-11",
        body={"nl": "Het officiële voorbeeldexamen van het CBR, met daarnaast de "
                    "woordenlijst en de «struikelblokken bij het examen»."}),
    ReadingRef(
        code="bpr", kind="law",
        title="Binnenvaartpolitiereglement (BPR)",
        publisher="wetten.overheid.nl (KOOP)", url="https://wetten.overheid.nl/BWBR0003628/",
        lang="nl", cost="free", official=True, themes=(), basis="units",
        source_id="bpr", match="Binnenvaartpolitiereglement",
        source="https://wetten.overheid.nl/BWBR0003628/", as_of="2026-09-11",
        body={"nl": "Het reglement waaruit het grootste deel van de wettelijke "
                    "bepalingen (35 van de 80 punten) komt: lichten, dagtekens, "
                    "geluidsseinen, marifoon, vaarregels, stilliggen, snelle "
                    "motorboten. Geen auteursrecht (Auteurswet art. 11)."}),
    ReadingRef(
        code="rpr", kind="law",
        title="Rijnvaartpolitiereglement 1995 (RPR)",
        publisher="wetten.overheid.nl (KOOP)", url="https://wetten.overheid.nl/BWBR0006923/",
        lang="nl", cost="free", official=True, themes=(), basis="units",
        source_id="rpr", match="Rijnvaartpolitiereglement",
        source="https://wetten.overheid.nl/BWBR0006923/", as_of="2026-09-11",
        body={"nl": "De Rijnregels, in het examen gevraagd «in het bijzonder voor "
                    "zover afwijkend van het BPR» (Rijn, Waal, Lek)."}),
    ReadingRef(
        code="svw", kind="law",
        title="Scheepvaartverkeerswet (SVW)",
        publisher="wetten.overheid.nl (KOOP)", url="https://wetten.overheid.nl/BWBR0004364/",
        lang="nl", cost="free", official=True, themes=(), basis="units",
        source_id="svw", match="Scheepvaartverkeerswet",
        source="https://wetten.overheid.nl/BWBR0004364/", as_of="2026-09-11",
        body={"nl": "De wet als basis van de scheepvaartreglementen: varen onder "
                    "invloed, ademtest, intrekking van het vaarbewijs."}),
    ReadingRef(
        code="binnenvaartwet", kind="law",
        title="Binnenvaartwet (BVW)",
        publisher="wetten.overheid.nl (KOOP)", url="https://wetten.overheid.nl/BWBR0023009/",
        lang="nl", cost="free", official=True, themes=(), basis="units",
        source_id="binnenvaartwet", match="Binnenvaartwet",
        source="https://wetten.overheid.nl/BWBR0023009/", as_of="2026-09-11",
        body={"nl": "Het belang van de BVW voor de recreatievaart: de "
                    "vaarbewijsplicht en haar grenzen."}),
    ReadingRef(
        code="varen_doe_je_samen", kind="guide",
        title="Varen doe je Samen! — kennisbank veilig varen",
        publisher="Rijkswaterstaat, provincies, KNRM, Watersportverbond e.a.",
        url=_VDJS, lang="nl", cost="free", official=True,
        themes=("vaarregels", "voortstuwing", "veiligheid", "marifoon_radar",
                "vaarwater", "manoeuvreren"), basis="toc",
        source=_VDJS, as_of="2026-09-11",
        body={"nl": "Gratis campagnemateriaal van de vaarwegbeheerders: "
                    "vaarregels, motoronderhoud, brandpreventie, reddingsvesten, "
                    "knooppunten, marifoonkaart. Geen examenstof, wel de praktijk "
                    "erachter."}),
    ReadingRef(
        code="anwb_cursusboek", kind="handbook",
        title="ANWB Cursusboek Klein Vaarbewijs I en II (30e druk)",
        publisher="ANWB / Uitgeverij Hollandia", url=_ANWB, lang="nl", cost="paid",
        official=False, themes=nl_themes.PERMIT_THEMES["KVB-2"], basis="toc",
        price="zie ANWB-webwinkel (ISBN 978 90 641 0807 5)",
        source="https://hollandia-boeken.nl/wp-content/uploads/2024/05/9789064108075_sample.pdf",
        as_of="2026-09-11",
        body={"nl": "Het meest verspreide cursusboek; de hoofdstukken volgen de "
                    "volgorde van de exameneisen (1 wetten en reglementen, 2 "
                    "techniek, veiligheid en milieu, 3 het vaarwater en het weer, "
                    "4 de praktijk van het varen; verdere hoofdstukken KVB2). "
                    "Geen aanbeveling — een voorbeeld van de commerciële boeken."}),
)

PATH: tuple[PathStep, ...] = (
    PathStep(
        code="age", source="Binnenvaartwet art. 27 lid 1 onder a", url=_WET27,
        as_of="2026-08-15",
        body={"nl": "Een vaarbewijs wordt niet afgegeven aan wie de leeftijd van "
                    "18 jaar nog niet heeft bereikt (Binnenvaartwet art. 27 lid 1 "
                    "onder a). Voor het afleggen van het theorie-examen zelf stelt "
                    "het CBR geen leeftijdsgrens — de grens zit op de afgifte."}),
    PathStep(
        code="medical", source="Binnenvaartbesluit art. 20 lid 2 en art. 26",
        url=_BESLUIT20, as_of="2026-08-15",
        body={"nl": "Voor het klein vaarbewijs volstaat een gezondheidsverklaring "
                    "(niet ouder dan 26 weken) in plaats van een geneeskundige "
                    "verklaring; een geneeskundig onderzoek blijft achterwege als "
                    "daaruit blijkt dat u lichamelijk en geestelijk voldoende "
                    "geschikt bent (Binnenvaartbesluit art. 20 lid 2, art. 26 "
                    "lid 1)."}),
    PathStep(
        code="application", source="Binnenvaartbesluit art. 20 lid 1",
        url=_BESLUIT20, as_of="2026-08-15",
        body={"nl": "Bij de aanvraag legt u de gezondheidsverklaring over en het "
                    "getuigschrift van het afgelegde examen (Binnenvaartbesluit "
                    "art. 20 lid 1). Het examen wordt afgenomen door het CBR "
                    "(Centraal Bureau Rijvaardigheidsbewijzen, "
                    "Binnenvaartregeling art. 1.1); het vaarbewijs zelf wordt door "
                    "de minister afgegeven."}),
    PathStep(
        code="fees", source="CBR — theorie-examen Klein Vaarbewijs I",
        url=_CBR_KVB1, as_of="2026-08-15", volatile=True,
        body={"nl": "Examengeld CBR: € 53,15 voor het theorie-examen Klein "
                    "Vaarbewijs I. Toeslagen voor extra tijd (€ 13,50) of "
                    "individuele begeleiding (€ 41,60) komen daar bovenop. De "
                    "kosten van een vaarschool of cursus staan hier los van."}),
    PathStep(
        code="validity", source="Binnenvaartregeling bijlage 7.3", url=_REGELING73,
        as_of="2026-08-15", volatile=True,
        body={"nl": "Het klein vaarbewijs wordt afgegeven volgens het model "
                    "\"klein vaarbewijs/ICC voor de binnenvaart\" en geldt daarmee "
                    "tevens als International Certificate for Operators of "
                    "Pleasure Craft (Binnenvaartregeling bijlage 7.3)."}),
)


# --- regional variance ---------------------------------------------------------
# The Netherlands has no provincial exam variance — the permit is national. What
# does vary is the *water*: the maritime-nature waters are the KVB II delta, and
# the Rhine branches run under the CCNR's own reglement.
REGIONS: dict[str, Region] = {
    "binnenwateren": Region(
        code="binnenwateren", name="Rivieren, kanalen en meren (BPR)", primary=True,
        note="Het landelijke BPR-gebied; klein vaarbewijs I volstaat."),
    "maritieme_wateren": Region(
        code="maritieme_wateren", name="Wateren van maritieme aard (KVB II)",
        note="Binnenvaartregeling art. 7.11b lid 2: " + ", ".join(MARITIEME_WATEREN)
             + ". Hier is klein vaarbewijs II vereist."),
    "rijn": Region(
        code="rijn", name="Rijn, Waal, Lek en Pannerdensch Kanaal (RPR)",
        note="Rijnvaartpolitiereglement 1995 (CCR) in plaats van het BPR; wijkt "
             "af van het BPR maar blijft op de CEVNI-basis."),
}
DEFAULT_REGION = "binnenwateren"


COUNTRY = Country(
    code="NL",
    name="Nederland",
    default_lang="nl",
    langs=("nl",),
    sources=tuple(SOURCES),
    themes=dict(nl_themes.THEMES),
    tagger=nl_themes.tag_theme,
    extension_themes=nl_themes.EXTENSION_THEMES,
    permits=PERMITS,
    regions=REGIONS,
    default_region=DEFAULT_REGION,
    references=REFERENCES,
    path=PATH,
    reading=READING,
    legal_basis=LEGAL_BASIS,
    # The Dutch code puts its most examinable rules in long articles (head-on,
    # crossing, small-craft lights, locks all exceed the default 2200-character
    # ceiling) and its sharpest ones in a single sentence, so the drafting window
    # is widened at both ends.
    draft_len=(60, 9000),
    # Only what the ministerial exam programme names — see nl_examscope.
    examinable=nl_examscope.examinable,
)
