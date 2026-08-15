"""Parser for BWB "toestand" XML (Dutch consolidated law, wetten.overheid.nl).

KOOP publishes every consolidated state of a Dutch act as a single XML document
under a plain, namespace-free DTD. The shape is close enough to the German
``gii-norm`` that this parser mirrors :mod:`parsers.gii` deliberately:

    <toestand bwb-id="BWBR0003628" inwerkingtreding="2026-06-17">
      <wetgeving>
        <citeertitel>Binnenvaartpolitiereglement</citeertitel>
        <hoofdstuk><kop><nr>5</nr><titel>Verkeerstekens</titel></kop>
          <artikel label="Artikel 5.01">
            <kop><label>Artikel</label><nr>5.01</nr><titel>…</titel></kop>
            <lid><lidnr>1</lidnr><al>…</al></lid>
          </artikel>
        </hoofdstuk>
        <bijlage label="Bijlage 7"><kop>…</kop>… <illustratie naam="65620.png"/></bijlage>

One ``<artikel>`` (or ``<bijlage>``) becomes one article-level
:class:`KnowledgeUnit`. Two details are load-bearing:

* **``<meta-data>`` must be stripped before flattening.** Every provision carries
  an amendment apparatus (``<brondata>``: Staatsblad year, number and three dates)
  inside the element. Flattening naively glues "2024 104 25-04-2024 …" onto the
  end of the legal text, which then reads as if it were part of the rule.
* **The chapter needs no separate lookup.** Every Dutch article number is already
  chapter-qualified — "Artikel 5.01" is in chapter 5, and across the whole BPR not
  one article label disagrees with the ``<hoofdstuk>`` it sits in. So the ref
  stays the citation a reader would actually write, and the theme tagger reads the
  chapter straight off it.

Dutch law is enacted in Dutch only, so — as for the German path — the theme
tagger runs directly on the single language with no cross-language propagation.
"""

from __future__ import annotations

import os
import re

from lxml import etree

from ..countries import nl_themes
from ..schema import Asset, KnowledgeUnit, make_id
from ..sources import Source

# Sub-kilobyte PNGs in the BWB annexes are inline glyphs and rule-lines, not
# plates. Same threshold and intent as the German parser.
_MIN_FIGURE_BYTES = 250

# Elements whose subtree is apparatus, never legal text.
_APPARATUS = ("meta-data", "redactie")


def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).replace("\xa0", " ").strip()


def _body_text(el) -> str:
    """Flattened legal text of a provision, amendment apparatus removed.

    Joining the text nodes (rather than concatenating ``itertext``) keeps a list
    marker and its clause from gluing together — "1°." + "schip: elk vaartuig…".
    """
    clone = etree.fromstring(etree.tostring(el))
    for tag in _APPARATUS:
        for node in list(clone.iter(tag)):
            parent = node.getparent()
            if parent is not None:
                parent.remove(node)
    for kop in clone.findall("kop"):          # the heading is carried separately
        clone.remove(kop)
    return _clean(" ".join(clone.itertext()))


def _heading(el) -> tuple[str, str]:
    """(number, title) from a provision's ``<kop>``."""
    kop = el.find("kop")
    if kop is None:
        return "", ""
    return _clean(kop.findtext("nr") or ""), _clean(kop.findtext("titel") or "")


def _abbrev(root) -> str:
    """The act's citation title (``<citeertitel>``), e.g. "Binnenvaartpolitiereglement"."""
    return _clean(root.findtext(".//citeertitel") or "")


def _assets(el, src_id: str, images: dict, ref: str, lang: str) -> list[Asset]:
    out: list[Asset] = []
    for i, im in enumerate(el.iter("illustratie"), start=1):
        name = im.get("naam") or ""
        meta = images.get(name)
        if not meta or meta.get("bytes", 0) < _MIN_FIGURE_BYTES:
            continue
        out.append(Asset(type="image",
                         path=_asset_path(src_id, meta["path"], lang),
                         caption=_clean(im.get("alt") or "") or f"{ref} – figuur {i}"))
    return out


def parse(src: Source, manifest: dict, tagger=None) -> list[KnowledgeUnit]:
    # `tagger` is the country's theme classifier; defaults to the Dutch one (BWB
    # is Dutch law), so passing country.tagger is a no-op for NL.
    tag_theme = tagger or nl_themes.tag_theme
    xml_path = os.path.join(os.path.dirname(__file__), "..", "..",
                            manifest["files"]["xml"]["path"])
    root = etree.parse(xml_path).getroot()
    images = manifest["files"].get("images", {})
    lang = manifest.get("lang", "nl")
    abbrev = _abbrev(root)

    prov = dict(source_id=src.id, source_name=src.name, source_url=src.url,
                retrieved=manifest["retrieved"],
                legal_version=manifest.get("legal_version", ""), licence=src.licence,
                lang=lang)

    # An act may be ingested for named provisions only (see Source.only_refs):
    # the exam programme cites one article of a 1307-article commercial code, and
    # pulling the other 1306 into a boating KB would drown it.
    keep = set(src.only_refs)

    units: list[KnowledgeUnit] = []
    seen: set[str] = set()
    for el in root.iter("artikel", "bijlage"):
        label = _clean(el.get("label") or "")
        if keep and label not in keep:
            continue
        nr, title = _heading(el)
        if not label:
            label = f"Bijlage {nr}" if el.tag == "bijlage" else f"Artikel {nr}"
        body = _body_text(el)
        if not body and not title:
            continue

        ref = f"{abbrev} {label}".strip()
        unit_id = make_id(src.id, ref, lang)
        if unit_id in seen:                    # defensive: labels repeat across parts
            continue
        seen.add(unit_id)

        theme = tag_theme(ref=ref, title=title, text=body,
                          default=src.default_theme)
        units.append(KnowledgeUnit(
            id=unit_id, theme=theme, kind="article", ref=ref, title=title,
            text=body, assets=_assets(el, src.id, images, ref, lang), **prov))
    return units


def _asset_path(source_id: str, raw_rel_path: str, lang: str = "nl") -> str:
    """Where the figure is published in the KB — mirrors the German/Swiss layout:
    non-FR languages are namespaced (data/assets/<source>/<lang>/<file>) so the
    normalize stage copies from the matching data/raw/<source>/<lang>/images/."""
    fname = os.path.basename(raw_rel_path)
    sub = source_id if lang == "fr" else os.path.join(source_id, lang)
    return os.path.join("data", "assets", sub, fname)
