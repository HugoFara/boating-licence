"""International / harmonised layer — the supra-national codes that sit *above*
the national exams in the regime tree (:mod:`src.jurisdictions`).

This is not a country with its own permits; it is the ingestion home for the
**harmonised navigation codes** that the per-country banks share — the bases
``COLREGS`` and ``CEVNI`` in the regime tree. Modelling it as a registry member
(code ``INT``) lets the ordinary fetch→parse→normalize pipeline ground those bases
in their *canonical* text, instead of only indirectly via national enactments
(KVR=COLREG, BinSchStrO≈CEVNI). It carries no permits and no playable bank, so the
player skips it (``run.py cmd_web`` shows only permit-bearing countries) and
:mod:`src.jurisdictions` skips generating national regime nodes for it.

Legal boundary (the project's hard rule — only public-domain / clearly-reusable):

* **COLREG — INGESTED.** The verbatim International Regulations (1972) are
  reproduced as a **US-Government work** by the US Coast Guard, hence public domain
  under 17 USC §105. We ingest the USCG "Navigation Rules" PDF and keep only its
  International pages (it prints International and US-Inland on facing pages); the
  IMO's own consolidated edition is copyrighted and is *not* used.
* **CEVNI — NOT INGESTED.** The canonical UNECE text (Resolution No. 24, now
  ECE/TRANS/SC.3/115/Rev.6) is **all-rights-reserved**: UN policy requires written
  permission to reproduce and forbids redistribution / derivative works. It fails
  the reuse bar, so it is recorded as a :class:`Reference` only; a reproduction-
  permission request has been sent to the rights holders (UNECE) and is pending.
  Until/unless granted,
  the CEVNI base stays grounded via the public-domain national inland enactments
  already ingested (CH ONI/RNL, DE BinSchStrO/RheinSchPV), which :mod:`src.scope`
  buckets into ``cevni``.
"""

from __future__ import annotations

from ..sources import Source
from . import intl_themes
from .base import Country, Reference, Region

LEGAL_BASIS = (
    "Harmonised codes. COLREG (International Regulations for Preventing Collisions "
    "at Sea, 1972) is ingested from the US Coast Guard reproduction — a "
    "US-Government work, public domain under 17 USC §105 (the IMO consolidated "
    "edition is copyrighted and is not used). CEVNI (UNECE Resolution No. 24) is "
    "all-rights-reserved (UN permission required) and is therefore NOT ingested: "
    "it is documented as a reference and the CEVNI base stays grounded via "
    "public-domain national inland enactments. A reproduction-permission request "
    "has been sent to UNECE and is pending a response from the rights owners.")

_COLREG_LICENCE = (
    "Public domain — US Government work (17 USC §105). Verbatim International "
    "Regulations (1972) as published by the US Coast Guard, navcen.uscg.gov. "
    "Attribution appreciated; reuse unrestricted.")

# The USCG "Navigation Rules" PDF: International + US-Inland on facing pages; the
# parser (src/parsers/colreg.py) keeps only the —INTERNATIONAL— pages, so the
# US-Inland enactment is never ingested. All 38 Rules + Annexes I–IV.
SOURCES: list[Source] = [
    Source(
        id="colreg", kind="pdf", lang="en",
        name="COLREG — International Regulations for Preventing Collisions at Sea, 1972",
        url="https://www.navcen.uscg.gov/sites/default/files/pdf/navRules/navrules.pdf",
        default_theme="general", licence=_COLREG_LICENCE),
]

REFERENCES: tuple[Reference, ...] = (
    Reference(
        name="CEVNI — European Code for Inland Waterways (UNECE Resolution No. 24, "
             "ECE/TRANS/SC.3/115/Rev.6)",
        url="https://unece.org/transport/publications/cevni-european-code-inland-waterways-rev6",
        note="The harmonised inland traffic code (the CEVNI base). NOT ingested: "
             "UNECE/UN material is all-rights-reserved — reproduction needs written "
             "permission and redistribution/derivatives are forbidden, so it fails "
             "the project's public-domain/clearly-reusable rule. The CEVNI base is "
             "instead grounded via the public-domain national inland enactments "
             "already ingested (CH ONI/RNL, DE BinSchStrO/RheinSchPV). A reproduction-"
             "permission request has been sent to the rights owners and is pending."),
)

# Not a within-country variance, just a single descriptive bucket: the codes here
# are supra-national by definition.
REGIONS: dict[str, Region] = {
    "global": Region(code="global", name="International (harmonised codes)",
                     primary=True,
                     note="Supra-national; applies above any national regime."),
}

COUNTRY = Country(
    code="INT",
    name="International (harmonised codes)",
    default_lang="en",
    langs=("en",),
    sources=tuple(SOURCES),
    themes=dict(intl_themes.THEMES),
    tagger=intl_themes.tag_theme,
    extension_themes=intl_themes.EXTENSION_THEMES,
    permits={},                       # sourcing-only layer: no exam, no player bundle
    regions=REGIONS,
    default_region="global",
    references=REFERENCES,
    legal_basis=LEGAL_BASIS,
)
