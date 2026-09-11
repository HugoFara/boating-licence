"""Reading layer: ship the *cited* law articles so the player can show the theory
a question is grounded in, offline, instead of only linking out to it.

Every approved question carries ``provenance.unit_id`` — the knowledge-base unit
(one article / annex item) it was derived from. The KB holds that unit's full
text, so the reading bundle is simply the subset of units at least one
exportable question in the target language cites. That keeps it small (a few
dozen KB per bank) and honest: nothing ships that no question points at, and
nothing is paraphrased — the article text is verbatim from the ingested source.

Licence gate: only units whose source licence permits verbatim redistribution
are exported (public-domain law, CC BY(-SA) references, Etalab / Licence
Ouverte). Anything else is skipped — the player still has the citation + URL on
the question, it just cannot show the text inline.
"""
from __future__ import annotations

import json
import os
import sqlite3

from . import schema as qschema

# Substrings (case-insensitive) that mark a KB unit licence as redistributable
# verbatim. Deliberately an allow-list: an unknown licence string ships nothing.
_REDISTRIBUTABLE = (
    "public domain",
    "cc by",                  # CC BY / CC BY-SA (attribution shipped with the unit)
    "licence ouverte",
    "open licence",
    "etalab",
    "freely reusable",
    "reuse with attribution",
    "gemeinfrei",
)


def redistributable(licence: str | None) -> bool:
    """True when the licence text names a term that allows verbatim reuse."""
    s = (licence or "").lower()
    return any(k in s for k in _REDISTRIBUTABLE)


def cited_unit_ids(qconn: sqlite3.Connection, lang: str,
                   exportable_only: bool = True) -> set[str]:
    """Unit ids cited by the (exportable) questions in one content language."""
    sql = "SELECT DISTINCT prov_unit_id FROM questions WHERE lang = ?"
    args: tuple = (lang,)
    if exportable_only:
        ph = ",".join("?" * len(qschema.EXPORTABLE_STATUSES))
        sql += f" AND review_status IN ({ph})"
        args += tuple(qschema.EXPORTABLE_STATUSES)
    return {r[0] for r in qconn.execute(sql, args) if r[0]}


def collect(qconn: sqlite3.Connection, kb_path: str, lang: str,
            exportable_only: bool = True) -> dict[str, dict]:
    """Resolve the cited unit ids against the KB and return the redistributable
    ones as ``{unit_id: {ref, title, text, source, url, licence, as_of, lang}}``.
    A missing KB (or a bank whose provenance ids don't map to KB units — e.g. a
    seed-driven bank or an official catalogue) yields an empty map."""
    ids = cited_unit_ids(qconn, lang, exportable_only)
    if not ids or not os.path.exists(kb_path):
        return {}
    kb = sqlite3.connect(kb_path)
    kb.row_factory = sqlite3.Row
    out: dict[str, dict] = {}
    try:
        wanted = sorted(ids)
        for start in range(0, len(wanted), 500):      # stay under SQLite's bind cap
            chunk = wanted[start:start + 500]
            ph = ",".join("?" * len(chunk))
            rows = kb.execute(
                "SELECT id, ref, title, text, source_name, source_url, licence, "
                "legal_version, retrieved, lang FROM units WHERE id IN (%s)" % ph,
                chunk).fetchall()
            for r in rows:
                text = (r["text"] or "").strip()
                if not text or not redistributable(r["licence"]):
                    continue
                out[r["id"]] = {
                    "ref": r["ref"] or "",
                    "title": r["title"] or "",
                    "text": text,
                    "source": r["source_name"] or "",
                    "url": r["source_url"] or "",
                    "licence": r["licence"] or "",
                    "as_of": r["legal_version"] or r["retrieved"] or "",
                    "lang": r["lang"] or "",
                }
    finally:
        kb.close()
    return out


def export_reading_json(qconn: sqlite3.Connection, kb_path: str, out_path: str,
                        lang: str, exportable_only: bool = True) -> int:
    """Write ``reading.<lang>.json`` — ``{"units": {unit_id: {...}}}`` — for the
    player's Learn tab. Returns the number of units written (0 ⇒ nothing was
    written; the caller ships no file and the player falls back to links)."""
    units = collect(qconn, kb_path, lang, exportable_only)
    if not units:
        return 0
    payload = {"meta": {"lang": lang, "count": len(units)}, "units": units}
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    return len(units)


# --- the "where to study" list -------------------------------------------------
# A ReadingRef with basis "units" is an ingested law: its theme list is not
# authored but derived from the themes the KB tagged its units with. The keyword
# tagger leaves a little noise on a long act (one "Wetterkunde" unit in a traffic
# ordinance), so a theme counts only when it holds at least MIN_UNITS units AND
# MIN_SHARE of the act — enough to be a subject the act actually treats.
MIN_UNITS = 3
MIN_SHARE = 0.02


def unit_themes(kb_path: str, source_id: str) -> list[str]:
    """Themes an ingested source substantively covers, by unit count (desc)."""
    if not source_id or not os.path.exists(kb_path):
        return []
    kb = sqlite3.connect(kb_path)
    try:
        rows = kb.execute("SELECT theme, COUNT(*) FROM units WHERE source_id = ? "
                          "GROUP BY theme ORDER BY COUNT(*) DESC", (source_id,)).fetchall()
    finally:
        kb.close()
    total = sum(n for _, n in rows)
    return [t for t, n in rows if n >= MIN_UNITS and n / total >= MIN_SHARE] if total else []


def manifest_for(country, kb_path: str, permit: str | None = None) -> list[dict]:
    """The country's reading list for a bundle manifest: ``basis == "units"``
    entries get their themes from the KB; with ``permit`` set (a bundle that is
    one permit/option and ships no permit table — France), entries scoped to
    other permits are dropped and the scope cleared so the player shows them."""
    out = []
    for ref in country.reading_manifest():
        scope = ref.get("permit_scope") or []
        if permit is not None:
            if scope and permit not in scope:
                continue
            ref["permit_scope"] = []
        if ref.get("basis") == "units" and not ref.get("themes"):
            ref["themes"] = unit_themes(kb_path, ref.get("source_id", ""))
        out.append(ref)
    return out
