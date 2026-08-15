"""European Union layer — the Union acts that sit *beside* the national exams.

A second supra-national member alongside :mod:`countries.intl`, and deliberately
distinct from it. INT holds the **traffic codes** (COLREG, and CEVNI if UNECE ever
clears it) — the rules of the road, which the regime tree orders by water. The EU
acts here are a different kind of law: they do not tell you who gives way, they
govern the **boat, its certificate and your qualification**, and they apply
Union-wide regardless of which water you are on.

That is why this layer adds **no new base** to :mod:`src.jurisdictions`. A design
category is not a third traffic code; it is portable content that holds under any
traffic code, which is exactly what the ``universal`` base already means — and
what :mod:`src.scope` already does with the French questions on CE categories. So
EU units ground ``universal`` and the tree is untouched.

Why it earns its place in a boating-licence trainer:

* **Directive 2013/53/EU** (recreational craft) is *directly examinable*. Its
  Annex I fixes the design categories A–D by wind force and significant wave
  height — the single most-asked "European" question in every national bank —
  plus the CE marking, the builder's plate and the craft identification number.
* **Directive (EU) 2016/1629** defines the Union inland navigation certificate
  and the classification of inland waterways (zones 1–4) that national permits
  refer to.
* **Directive (EU) 2017/2397** is the reason a Dutch, German or French inland
  certificate is recognised across the Union. The Dutch acts ingested under
  :mod:`countries.nl` cite it on nearly every page.

Legal boundary — this passes the project's reuse bar more cleanly than any other
source it has:

* **EUR-Lex — INGESTED.** The Publications Office states that reuse of the legal
  documents published in EUR-Lex is authorised for commercial and non-commercial
  purposes under **Commission Decision 2011/833/EU**; the editorial content and
  consolidated texts are additionally licensed **CC BY 4.0**, and the metadata is
  **CC0**. Attribution is required; nothing else is.
* **What is NOT ingested:** the harmonised standards the directives refer to
  (the EN ISO series behind "presumption of conformity"). Those are CEN/ISO
  works, sold per copy and all-rights-reserved. Only the directives' own text is
  used; a standard is never quoted, only named as the act names it.

This member carries no permits, so — like INT — the player skips it and
:mod:`src.jurisdictions` generates no national regime node for it.
"""

from __future__ import annotations

from ..sources import Source
from . import eu_themes
from .base import Country, Reference, Region

LEGAL_BASIS = (
    "EU law from EUR-Lex. The Publications Office authorises reuse of the legal "
    "documents published in EUR-Lex for commercial and non-commercial purposes "
    "under Commission Decision 2011/833/EU; editorial content and consolidated "
    "texts are licensed CC BY 4.0 and the metadata is CC0. Attribution to the "
    "European Union is required and is carried per unit. The harmonised EN ISO "
    "standards the directives cite are CEN/ISO works, all-rights-reserved, and "
    "are therefore never reproduced — only named as the directive names them.")

_EURLEX_LICENCE = (
    "© European Union, 1998-2026 — reuse authorised under Commission Decision "
    "2011/833/EU (commercial and non-commercial); consolidated text CC BY 4.0. "
    "Source: eur-lex.europa.eu. Attribution required.")

# kind="eurlex": one CELEX, 24 official-language expressions. The fetcher resolves
# the newest *consolidated* version, so the KB tracks the text in force.
SOURCES: list[Source] = [
    Source(
        id="rcd", kind="eurlex", lang="en", celex="32013L0053",
        name="Directive 2013/53/EU on recreational craft and personal watercraft",
        url="https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32013L0053",
        default_theme="craft_design", licence=_EURLEX_LICENCE),
    Source(
        id="iwt_tech", kind="eurlex", lang="en", celex="32016L1629",
        name="Directive (EU) 2016/1629 laying down technical requirements for "
             "inland waterway vessels",
        url="https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32016L1629",
        default_theme="vessel_certification", licence=_EURLEX_LICENCE),
    Source(
        id="iwt_quals", kind="eurlex", lang="en", celex="32017L2397",
        name="Directive (EU) 2017/2397 on the recognition of professional "
             "qualifications in inland navigation",
        url="https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32017L2397",
        default_theme="qualifications", licence=_EURLEX_LICENCE),
]

REFERENCES: tuple[Reference, ...] = (
    Reference(
        name="Harmonised standards under Directive 2013/53/EU (EN ISO series)",
        url="https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32013L0053",
        note="The standards that give 'presumption of conformity' (stability, "
             "buoyancy, freeboard, fuel systems…). NOT ingested: CEN/ISO works are "
             "sold per copy and all-rights-reserved, failing the project's "
             "public-domain / clearly-reusable rule. The directive's own reference "
             "to them is ingested; their text never is."),
    Reference(
        name="UNECE Resolution No. 40 — International Certificate for Operators of "
             "Pleasure Craft (ICC)",
        url="https://unece.org/transport/inland-water-transport/"
            "international-certificate-operators-pleasure-craft",
        note="Not EU law but the instrument that makes a national pleasure-craft "
             "licence travel: the Dutch klein vaarbewijs is issued on the "
             "'klein vaarbewijs/ICC' model (Binnenvaartregeling bijlage 7.3) and "
             "France issues an ICC to permit holders (Code des transports). Like "
             "CEVNI it is UNECE material and all-rights-reserved, so it is "
             "documented rather than ingested."),
)

# Not a within-country variance: these acts apply Union-wide by construction.
REGIONS: dict[str, Region] = {
    "union": Region(code="union", name="European Union / EEA", primary=True,
                    note="Applies Union-wide; EEA states apply the same acts "
                         "through the EEA Agreement."),
}

COUNTRY = Country(
    code="EU",
    name="European Union (Union acts)",
    default_lang="en",
    # The acts exist in all 24 official languages; these are the ones the project
    # builds banks in today, and each is an equally authentic text of the same act.
    langs=("en", "nl", "de", "fr", "it"),
    sources=tuple(SOURCES),
    themes=dict(eu_themes.THEMES),
    tagger=eu_themes.tag_theme,
    extension_themes=eu_themes.EXTENSION_THEMES,
    permits={},                       # sourcing-only layer: no exam, no player bundle
    regions=REGIONS,
    default_region="union",
    references=REFERENCES,
    legal_basis=LEGAL_BASIS,
)
