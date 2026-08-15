"""Parser for EUR-Lex act HTML (EU directives and regulations).

EUR-Lex marks every article with an ELI-derived skeleton that is stable across
languages and act types, which is what makes this parseable without heuristics:

    <div class="eli-subdivision" id="art_12">
      <p class="oj-ti-art">Article 12</p>
      <div class="eli-title" id="art_12.tit_1"><p class="oj-sti-art">Free movement</p></div>
      <p class="oj-normal">…</p>

Articles carry ``id="art_N"``; recitals are ``rct_N`` and citations ``cit_N``.
**Recitals and citations are skipped.** They are the legislator's reasoning, not
the enacted rule, and a study KB that mixed them in would quote a "whereas"
clause as if it bound anyone.

Two things are less tidy than that skeleton suggests, and both are handled here:

* **There are two renditions of the same act.** The Official Journal one puts
  paragraph text in ``<p class="oj-normal">`` under ``oj-ti-art`` headings; the
  *consolidated* one puts it in ``<div class="norm">`` under
  ``title-article-norm``. Reading only one of them silently returns an article
  whose body is just its own heading, so :func:`_flatten` collects text nodes
  rather than any single tag.
* **Annexes sit outside the skeleton** — no ids, just a run of text after the
  last article. They are split off by the Official Journal's own typographic
  rule: the word for "annex" in CAPITALS ("ANNEX I", "BIJLAGE I", "ANHANG I")
  heads an annex, while the same word in title case only cross-references one.
  Worth the trouble, because the Recreational Craft Directive's examinable
  content — the design categories A–D with their wind force and wave height —
  lives in Annex I and in no article at all.

The same CELEX in another language is the same document with the same ids, and
the refs emitted here are language-neutral, so one act yields one unit set per
language with matching refs.
"""

from __future__ import annotations

import os
import re

from lxml import html as lxml_html

from ..countries import eu_themes
from ..schema import KnowledgeUnit, make_id
from ..sources import Source

# The enacted text: articles, the enacting-terms lead-in, and nothing else.
_ARTICLE_ID = re.compile(r"^art_(\d+)$")

def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).replace("\xa0", " ").strip()


def _flatten(el) -> str:
    """All text under a node, markup-agnostic.

    EUR-Lex serves an act in two different renditions and the parser has to read
    both: the OJ rendition puts paragraph text in ``<p class="oj-normal">``, the
    consolidated one in ``<div class="norm">``. Collecting the text nodes instead
    of any one tag reads both, and joining on them (rather than concatenating)
    keeps adjacent blocks from gluing together.

    Tables are flattened first, cells separated by "·", because in these acts a
    table is often the rule itself — the design-category grid (category / wind
    force / significant wave height) would otherwise read as one run-on line.
    """
    clone = lxml_html.fromstring(lxml_html.tostring(el))
    for tbl in clone.xpath(".//table[not(ancestor::table)]"):
        cells = [_clean(" ".join(c.itertext())) for c in tbl.iter("td", "th")]
        repl = lxml_html.Element("p")
        repl.text = " " + " · ".join(c for c in cells if c) + " "
        repl.tail = tbl.tail
        parent = tbl.getparent()
        if parent is not None:
            parent.replace(tbl, repl)
    return _clean(" ".join(clone.itertext()))


# Article label / subtitle paragraph classes: the OJ rendition on the left, the
# consolidated rendition on the right.
_LABEL_CLASSES = ("oj-ti-art", "title-article-norm")
_SUBTITLE_CLASSES = ("oj-sti-art", "stitle-article-norm")


def _has(p, classes: tuple[str, ...]) -> bool:
    cls = p.get("class") or ""
    return any(c in cls for c in classes)


def _title_of(div) -> str:
    """The article's own subtitle ("Free movement"), in either rendition."""
    for p in div.iter("p"):
        if _has(p, _SUBTITLE_CLASSES):
            return _clean(" ".join(p.itertext()))
    return ""


def _article_body(div) -> str:
    """The article's text minus its own label and subtitle paragraphs."""
    clone = lxml_html.fromstring(lxml_html.tostring(div))
    for p in list(clone.iter("p")):
        if _has(p, _LABEL_CLASSES) or _has(p, _SUBTITLE_CLASSES):
            parent = p.getparent()
            if parent is not None:
                parent.remove(p)
    return _flatten(clone)


# An annex heading is the act's own word for "annex" in CAPITALS followed by its
# numeral. That is the Official Journal's typographic convention and it separates
# a heading from a cross-reference cleanly in every language: "ANNEX I" heads an
# annex, "Annex I"/"bijlage I" only points at one. Checked against four acts in
# two languages: it finds every annex and nothing else.
_ANNEX_HEAD = re.compile(
    r"\b(?:ANNEX|ANNEXE|BIJLAGE|ANHANG|ALLEGATO|ANEXO)\b\s*([IVXLC]+|\d+)?")


def _annexes(root) -> list[tuple[str, str, str]]:
    """[(ref label, title, body)] split off the tail of the flattened document."""
    flat = _flatten(root)
    marks = list(_ANNEX_HEAD.finditer(flat))
    out: list[tuple[str, str, str]] = []
    for n, m in enumerate(marks):
        end = marks[n + 1].start() if n + 1 < len(marks) else len(flat)
        body = _clean(flat[m.end():end])
        if not body:
            continue
        numeral = (m.group(1) or "").upper()
        # The first sentence-ish run is the annex's own heading text.
        title = _clean(body[:120].split(".")[0])
        out.append((f"Annex {numeral}".strip(), title, body))
    return out


def parse(src: Source, manifest: dict, tagger=None) -> list[KnowledgeUnit]:
    tag_theme = tagger or eu_themes.tag_theme
    path = os.path.join(os.path.dirname(__file__), "..", "..",
                        manifest["files"]["html"]["path"])
    with open(path, "rb") as fh:
        root = lxml_html.fromstring(fh.read())
    lang = manifest.get("lang", "en")
    celex = manifest.get("celex", "") or src.celex

    prov = dict(source_id=src.id, source_name=src.name, source_url=src.url,
                retrieved=manifest["retrieved"],
                legal_version=manifest.get("legal_version", ""), licence=src.licence,
                lang=lang)

    # A short act citation for refs: "Directive 2013/53/EU" -> "2013/53/EU".
    short = _short_cite(src.name, celex)

    units: list[KnowledgeUnit] = []
    for div in root.iter("div"):
        if "eli-subdivision" not in (div.get("class") or ""):
            continue
        m = _ARTICLE_ID.match(div.get("id") or "")
        if not m:                              # recitals/citations: not enacted text
            continue
        title = _title_of(div)
        body = _article_body(div)
        if not body and not title:
            continue
        # The ref is deliberately language-NEUTRAL ("art. 12", not the localised
        # "Artikel 12"/"Article 12"), so the same provision carries the same ref
        # in all 24 expressions and cross-language links line up by ref alone.
        ref = f"{short} art. {m.group(1)}"
        units.append(KnowledgeUnit(
            id=make_id(src.id, ref, lang), theme=tag_theme(
                ref=ref, title=title, text=body, default=src.default_theme),
            kind="article", ref=ref, title=title, text=body, **prov))

    for label, title, body in _annexes(root):
        ref = f"{short} {label}"
        units.append(KnowledgeUnit(
            id=make_id(src.id, ref, lang), theme=tag_theme(
                ref=ref, title=title, text=body, default=src.default_theme),
            kind="article", ref=ref, title=title, text=body, **prov))
    return units


# No \b before "(EU)" — see eu_themes._ACT for why that boundary never fires.
_ACT_NUM = re.compile(r"(\b\d{4}/\d{1,4}/[A-Z]{2,3}|\(EU\)\s*\d{4}/\d{1,4})")


def _short_cite(name: str, celex: str) -> str:
    """The citation people actually write: "Directive 2013/53/EU". Falls back to
    the CELEX when the source name carries no act number."""
    m = _ACT_NUM.search(name or "")
    if not m:
        return celex or "EU"
    kind = "Regulation" if celex[5:6] == "R" else "Directive"
    return f"{kind} {_clean(m.group(1))}"
