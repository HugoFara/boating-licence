"""Parser for the COLREG International Rules (the USCG public-domain PDF).

The US Coast Guard "Navigation Rules" PDF reproduces the **verbatim International
Regulations (1972)** as a US-Government work (public domain, 17 USC §105). Its
layout is page-based, not column-based: every page is headed either
``—INTERNATIONAL—`` or ``—INLAND—`` (never both), and the International pages
carry all 38 Rules + Annexes I–V. So we keep only the International pages and drop
the Inland enactment entirely.

On every International page the first two non-empty lines are boilerplate — the
``—INTERNATIONAL—`` marker and a running head (the Part's friendly name, e.g.
"Steering and Sailing Rules" / "ANNEX I -") — and the last line is a bare page
number. Stripping those per page (before concatenating) keeps the running head
from leaking into a Rule that spans a page break. A standalone ``RULE N`` line
opens a unit (its next line is the title); ``RULE N—CONTINUED`` / ``ANNEX
X—Continued`` are continuation markers and are dropped so the body flows; ``PART``
/ ``Section`` structural headers are dropped (the Part is recovered from the rule
number by :mod:`countries.intl_themes`).
"""

from __future__ import annotations

import os
import re

from ..countries import intl_themes
from ..schema import KnowledgeUnit, make_id
from ..sources import Source

# Page headers that classify a page's regime. International pages only.
_INTL = "—INTERNATIONAL—"
_INLAND = "—INLAND—"

# Line classifiers (matched on the stripped line).
_MARKER = re.compile(r"^—\s*(INTERNATIONAL|INLAND)\s*—$", re.I)
_PAGE_NO = re.compile(r"^\d{1,3}$")
_RULE = re.compile(r"^RULE\s+(\d+)\s*$", re.I)                 # opens a unit
_RULE_CONT = re.compile(r"^RULE\s+\d+\s*[—–-]\s*CONTINUED", re.I)
_ANNEX = re.compile(r"^ANNEX\s+([IVX]+)\b\s*[-—–]?\s*$", re.I)  # opens a unit
_ANNEX_CONT = re.compile(r"^ANNEX\s+[IVX]+\s*[—–-]\s*CONTINUED", re.I)
_STRUCT = re.compile(r"^(PART\s+[A-E]\b|Section\s+[IVX]+\b)", re.I)


def _intl_pages(doc) -> list[int]:
    """Page numbers whose header is —INTERNATIONAL— (and not —INLAND—)."""
    out = []
    for pno in range(doc.page_count):
        t = doc[pno].get_text()
        if _INTL in t and _INLAND not in t:
            out.append(pno)
    return out


def _clean_lines(doc, pages: list[int]) -> list[str]:
    """The content lines across the International pages, in order, with the
    per-page boilerplate (marker, running head, page number) and the structural /
    continuation headers removed.

    The Rules carry an in-body ``RULE N`` marker, but the Annexes do not: an
    annex's identity lives only in the page running head (line 1, e.g.
    ``ANNEX I -``). So when line 1 is an annex-start running head we inject a
    normalized ``ANNEX <roman>`` marker into the stream (its title is the next
    line); a rule-part running head or an annex *continuation* head is dropped."""
    out: list[str] = []
    for pno in pages:
        raw = [ln.strip() for ln in doc[pno].get_text().splitlines() if ln.strip()]
        if not raw:
            continue
        body = raw
        if _MARKER.match(raw[0]):              # line 0 marker + line 1 running head
            head = raw[1] if len(raw) > 1 else ""
            m = _ANNEX.match(head)
            if m and not _ANNEX_CONT.match(head):
                out.append(f"ANNEX {m.group(1).upper()}")   # open an annex unit
            body = raw[2:]
        for ln in body:
            if _PAGE_NO.match(ln) or _MARKER.match(ln):
                continue
            if _RULE_CONT.match(ln) or _ANNEX_CONT.match(ln) or _STRUCT.match(ln):
                continue
            out.append(ln)
    return out


def _roman(s: str) -> int:
    vals = {"I": 1, "V": 5, "X": 10}
    total = prev = 0
    for ch in reversed(s.upper()):
        v = vals.get(ch, 0)
        total += -v if v < prev else v
        prev = max(prev, v)
    return total


def parse(src: Source, manifest: dict) -> list[KnowledgeUnit]:
    import fitz                                  # PyMuPDF (declared in requirements)

    pdf_path = os.path.join(os.path.dirname(__file__), "..", "..",
                            manifest["files"]["pdf"]["path"])
    lang = manifest.get("lang", "en")
    doc = fitz.open(pdf_path)
    lines = _clean_lines(doc, _intl_pages(doc))

    prov = dict(source_id=src.id, source_name=src.name, source_url=src.url,
                retrieved=manifest["retrieved"],
                legal_version=manifest.get("legal_version", ""), licence=src.licence,
                lang=lang)

    units: list[KnowledgeUnit] = []
    ref = title = ""
    theme = ""
    buf: list[str] = []

    def flush():
        if not ref:
            return
        text = re.sub(r"\s+", " ", " ".join(buf)).strip()
        if not text and not title:
            return
        units.append(KnowledgeUnit(
            id=make_id(src.id, ref, lang), theme=theme, kind="article",
            ref=ref, title=title, text=text, assets=[], cross_refs=[], **prov))

    i = 0
    while i < len(lines):
        ln = lines[i]
        m_rule = _RULE.match(ln)
        m_annex = _ANNEX.match(ln)
        if m_rule:
            flush()
            n = int(m_rule.group(1))
            ref, theme = f"COLREG Rule {n}", intl_themes.theme_for_rule(n)
            title = lines[i + 1] if i + 1 < len(lines) else ""
            buf = []
            i += 2                              # consume the rule marker + its title
            continue
        if m_annex:
            flush()
            roman = m_annex.group(1).upper()
            ref, theme = f"COLREG Annex {roman}", "annexes"
            title = lines[i + 1] if i + 1 < len(lines) else ""
            buf = []
            i += 2
            continue
        buf.append(ln)
        i += 1
    flush()
    return units
