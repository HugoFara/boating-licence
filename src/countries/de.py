"""Germany — recreational-boating theory exams (Sportbootführerschein system).

Defined natively against :mod:`countries.base`. Two things make Germany a much
richer target than the Swiss original:

* **Federal law is machine-readable and public-domain.** gesetze-im-internet.de
  serves every ordinance as structured XML at ``<slug>/xml.zip`` (the German
  analogue of Fedlex). Federal law is free of copyright under **§5(1) UrhG**.
  These are the ``kind="gii"`` sources below, ingested by the law pipeline.
* **The official question catalogues are very likely free to reuse**
  (§5(2) UrhG — *amtliche Werke*; verbatim + attribution + no modification),
  unlike the off-limits Swiss asa bank. They are recorded as :class:`Reference`
  entries (the legal finding lives in code) but are NOT ingested in this task —
  that is a dedicated follow-up.

Confidence: source URLs/slugs and §5 status are high-confidence. Exam minute
counts and some block minima are school-sourced (medium) — each is flagged in the
relevant ``note`` rather than presented as settled fact, matching the project's
honesty rule for unverified numbers.
"""

from __future__ import annotations

from ..sources import Source
from . import de_themes
from .base import Country, ExamBlock, ExamRules, Permit, Reference, Region

# --- 2025–26 reform, still in flux (show as "pending", never as settled law) ---
REFORM_NOTE = (
    "Reform 2025–26 (BMV): Führerscheinpflicht einheitlich ab 11,03 kW (15 PS) "
    "unabhängig von der Antriebsart — die gesonderte 7,5-kW-Grenze für "
    "Elektromotoren soll wieder entfallen. Im Entwurf zudem: Ersatz des amtlichen "
    "SBF durch anerkannte Verbandsscheine (Zielhorizont ~2028). Noch nicht "
    "abgeschlossen — als ausstehend behandeln.")

LEGAL_BASIS = (
    "Bundesrecht (SeeSchStrO, BinSchStrO, KVR, SpFV, RheinSchPV) ist gemeinfrei "
    "nach §5(1) UrhG. Die amtlichen ELWIS-Fragenkataloge (SBF See/Binnen) sind "
    "sehr wahrscheinlich amtliche Werke nach §5(2) UrhG: wörtliche Wiedergabe mit "
    "Quellenangabe und ohne Änderung zulässig.")


# --- federal law (kind="gii": gesetze-im-internet.de/<slug>/xml.zip) -----------
_GII_LICENCE = "Public domain — German federal law (§5(1) UrhG, freely reusable)."

SOURCES: list[Source] = [
    Source(
        id="seeschstro", kind="gii", lang="de", gii_slug="seeschstro_1971",
        name="Seeschifffahrtsstraßen-Ordnung (SeeSchStrO)",
        url="https://www.gesetze-im-internet.de/seeschstro_1971/",
        default_theme="verkehrsregeln", licence=_GII_LICENCE),
    Source(
        id="binschstro", kind="gii", lang="de", gii_slug="binschstro_2012",
        name="Binnenschifffahrtsstraßen-Ordnung (BinSchStrO)",
        url="https://www.gesetze-im-internet.de/binschstro_2012/",
        default_theme="verkehrsregeln", licence=_GII_LICENCE),
    Source(
        id="kvr", kind="gii", lang="de", gii_slug="seestro_1972",
        name="Internationale Regeln zur Verhütung von Zusammenstößen auf See (KVR/COLREG)",
        url="https://www.gesetze-im-internet.de/seestro_1972/",
        default_theme="verkehrsregeln", licence=_GII_LICENCE),
    Source(
        id="spfv", kind="gii", lang="de", gii_slug="spfv",
        name="Sportbootführerscheinverordnung (SpFV)",
        url="https://www.gesetze-im-internet.de/spfv/",
        default_theme="recht_dokumente", licence=_GII_LICENCE),
    Source(
        id="rheinschpv", kind="gii", lang="de", gii_slug="rheinschpv_1994",
        name="Rheinschifffahrtspolizeiverordnung (RheinSchPV)",
        url="https://www.gesetze-im-internet.de/rheinschpv_1994/",
        default_theme="verkehrsregeln", licence=_GII_LICENCE),
]


# --- the official question catalogues (INGESTED — see src/questions/elwis.py) --
# The ELWIS Nutzungsbedingungen grant reuse explicitly: content may be reused,
# even commercially, "solange der Inhalt unverändert bleibt und als Quelle
# www.elwis.de angegeben wird" (≈ §5(2) UrhG amtliches Werk). So these are
# ingested verbatim with attribution by `run.py questions --country DE`; the URLs
# here are the canonical landing pages (the ingester discovers the section pages).
_CATALOG_NOTE = ("Amtliches Werk (§5(2) UrhG) — wörtlich + mit Quellenangabe "
                 "(www.elwis.de) + ohne Änderung wiederverwendbar. Ingestiert "
                 "durch run.py questions --country DE (src/questions/elwis.py).")

REFERENCES: tuple[Reference, ...] = (
    Reference(
        name="Amtlicher Fragenkatalog SBF See (≈300 Fragen)",
        url="https://www.elwis.de/DE/Sportschifffahrt/Sportbootfuehrerscheine/"
            "Fragenkatalog-See/Fragenkatalog-See-neu-node.html",
        note=_CATALOG_NOTE),
    Reference(
        name="Amtlicher Fragenkatalog SBF Binnen (≈300 Fragen)",
        url="https://www.elwis.de/DE/Sportschifffahrt/Sportbootfuehrerscheine/"
            "Fragenkatalog-Binnen/Fragenkatalog-Binnen-neu-node.html",
        note=_CATALOG_NOTE),
    Reference(
        name="Fragenkatalog SKS (Sportküstenschifferschein)",
        url="https://www.elwis.de/DE/Sportschifffahrt/Sportbootfuehrerscheine/"
            "Fragenkatalog-SKS/Fragenkatalog-SKS-node.html",
        note=_CATALOG_NOTE + " §5-Status etwas schwächer (DSV/DMYV-Mitautorschaft)."),
    Reference(
        name="Bodensee-Schifffahrts-Ordnung (BSO)",
        url="https://www.gesetze-bayern.de/Content/Document/BayBodSchO",
        note="Länder-/Staatsvertragsrecht (DE/AT/CH); nur auf Landesportalen als "
             "PDF/HTML, kein gii-XML. Für Bodensee-Patent maßgeblich."),
)


# --- recreational permits ------------------------------------------------------
def _basis(count: int = 7, min_correct: int = 5) -> ExamBlock:
    return ExamBlock("Basisfragen", count, min_correct)


PERMITS: dict[str, Permit] = {
    # Federal SBF — mandatory above 11.03 kW (15 PS). Binnen is split by drive.
    "SBF-Binnen-Motor": Permit(
        code="SBF-Binnen-Motor", label="Sportbootführerschein Binnen (Motor)",
        themes=de_themes.PERMIT_THEMES["SBF-Binnen-Motor"], drive="motor",
        exam=ExamRules(questions=30, time_limit_min=45, scoring="blocks",
                       blocks=(_basis(), ExamBlock("Spezifisch Binnen", 23, 18)),
                       note="7 Basis + 23 spezifisch; bestehen: ≥5 Basis & ≥18 spez.")),
    "SBF-Binnen-Motor-Segeln": Permit(
        code="SBF-Binnen-Motor-Segeln",
        label="Sportbootführerschein Binnen (Motor und Segeln)",
        themes=de_themes.PERMIT_THEMES["SBF-Binnen-Motor-Segeln"], drive="motor+sail",
        exam=ExamRules(questions=37, time_limit_min=60, scoring="blocks",
                       blocks=(_basis(), ExamBlock("Spezifisch Binnen", 23, 18),
                               ExamBlock("Spezifisch Segeln", 7, 5)),
                       note="7 Basis + 23 Binnen + 7 Segeln.")),
    "SBF-Binnen-Segeln": Permit(
        code="SBF-Binnen-Segeln", label="Sportbootführerschein Binnen (Segeln)",
        themes=de_themes.PERMIT_THEMES["SBF-Binnen-Segeln"], drive="sail",
        exam=ExamRules(questions=25, time_limit_min=35, scoring="blocks",
                       blocks=(_basis(4, 0), ExamBlock("Spezifisch Binnen", 14, 0),
                               ExamBlock("Spezifisch Segeln", 7, 0)),
                       note="Bestehen: insgesamt ≥20 von 25 (keine festen "
                            "Teilminima); min_correct=0 = kein eigenständiges Minimum.")),
    "SBF-See": Permit(
        code="SBF-See", label="Sportbootführerschein See",
        themes=de_themes.PERMIT_THEMES["SBF-See"], drive="motor+sail",
        exam=ExamRules(questions=30, time_limit_min=60, scoring="blocks",
                       blocks=(_basis(), ExamBlock("Spezifisch See", 23, 18)),
                       note="7 Basis + 23 See, dazu eine Navigationsaufgabe mit "
                            "Seekartenausschnitt (9 Fragen). Minutenzahl näherungsweise.")),
    # Voluntary higher certificates (commercially required only).
    "SKS": Permit(
        code="SKS", label="Sportküstenschifferschein (SKS)",
        themes=de_themes.PERMIT_THEMES["SKS"], drive="motor+sail", mandatory=False,
        exam=ExamRules(questions=30, time_limit_min=90, scoring="blocks",
                       blocks=(ExamBlock("Navigation", 9, 0),
                               ExamBlock("Seerecht", 7, 0),
                               ExamBlock("Wetterkunde", 5, 0),
                               ExamBlock("Seemannschaft", 9, 0)),
                       note="Küste bis 12 sm; setzt SBF See voraus. Plus separate "
                            "Kartenaufgabe. Teilminima/Detailstruktur: mittlere Sicherheit."),
        note="Freiwillig (gewerblich erforderlich)."),
    "SSS": Permit(
        code="SSS", label="Sportseeschifferschein (SSS)",
        themes=de_themes.PERMIT_THEMES["SSS"], drive="motor+sail", mandatory=False,
        exam=ExamRules(questions=0, time_limit_min=0, scoring="blocks",
                       note="Bis 30 sm + Nord-/Ostsee, Mittelmeer u. a. Struktur "
                            "nach DSV-Richtlinien; kein frei veröffentlichter "
                            "amtlicher Katalog gefunden — §5-Wiederverwendung "
                            "unsicher (niedrige Sicherheit)."),
        note="Freiwillig; Katalog-Wiederverwendung rechtlich nicht gesichert."),
    "SHS": Permit(
        code="SHS", label="Sporthochseeschifferschein (SHS)",
        themes=de_themes.PERMIT_THEMES["SHS"], drive="motor+sail", mandatory=False,
        exam=ExamRules(questions=0, time_limit_min=0, scoring="blocks",
                       note="Weltweit/unbegrenzt; setzt SSS voraus. Wie SSS: kein "
                            "frei veröffentlichter amtlicher Katalog — §5 unsicher."),
        note="Freiwillig; Katalog-Wiederverwendung rechtlich nicht gesichert."),
    # Bodensee-Schifferpatent — trinational (DE/AT/CH) regime under the BSO, the
    # German parallel to the project's shared-lake (Lac Léman) origin.
    "Bodensee-A": Permit(
        code="Bodensee-A", label="Bodensee-Schifferpatent Kategorie A (Motor)",
        themes=de_themes.PERMIT_THEMES["Bodensee-A"], drive="motor",
        exam=ExamRules(questions=0, time_limit_min=0, scoring="blocks",
                       note="Trinationales BSO-Patent; Pflicht ab >4,4 kW. Eigene "
                            "Prüfung der Anrainerstellen — nicht der Bund-SBF."),
        note="Bodensee (DE/AT/CH); ausgestellt von den Landratsämtern am See."),
    "Bodensee-D": Permit(
        code="Bodensee-D", label="Bodensee-Schifferpatent Kategorie D (Segel)",
        themes=de_themes.PERMIT_THEMES["Bodensee-D"], drive="sail",
        exam=ExamRules(questions=0, time_limit_min=0, scoring="blocks",
                       note="Trinationales BSO-Patent; Pflicht ab Segelfläche "
                            ">12 m². Eigene Prüfung der Anrainerstellen."),
        note="Bodensee (DE/AT/CH); ausgestellt von den Landratsämtern am See."),
}


# --- regional variance ---------------------------------------------------------
REGIONS: dict[str, Region] = {
    "national": Region(code="national", name="Bundesweit (SBF See/Binnen)",
                       primary=True,
                       note="Föderal einheitlich nach SpFV; keine Länder-Varianz."),
    "bodensee": Region(code="bodensee", name="Bodensee (BSO, DE/AT/CH)",
                       note="Eigenes trinationales Patent-Regime; ersetzt am See "
                            "den Bund-SBF (niedrigere Leistungsschwelle 4,4 kW)."),
}
DEFAULT_REGION = "national"


COUNTRY = Country(
    code="DE",
    name="Deutschland",
    default_lang="de",
    langs=("de",),
    sources=tuple(SOURCES),
    themes=dict(de_themes.THEMES),
    tagger=de_themes.tag_theme,
    extension_themes=de_themes.EXTENSION_THEMES,
    permits=PERMITS,
    regions=REGIONS,
    default_region=DEFAULT_REGION,
    references=REFERENCES,
    legal_basis=LEGAL_BASIS,
)
