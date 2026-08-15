"""Stage 1 — fetch raw sources to disk, verbatim, with provenance.

Each source caches under data/raw/<id>/ alongside a manifest.json recording the
exact URLs, retrieval date and (for law) the consolidated "état le" version.
Nothing re-fetches if the cache exists unless force=True, so stages stay cheap
and re-runnable. Fedlex is JS-rendered, so we never touch the page HTML: we
resolve structured files (Akoma Ntoso XML + PDF/A) via the SPARQL endpoint.
"""

from __future__ import annotations

import datetime as _dt
import io
import json
import os
import re
import time
import urllib.parse
import zipfile

import requests

from .sources import Source, SOURCES

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
SPARQL = "https://fedlex.data.admin.ch/sparqlendpoint"
GII_BASE = "https://www.gesetze-im-internet.de"
BWB_BASE = "https://repository.officiele-overheidspublicaties.nl/bwb"
EURLEX_BASE = "https://eur-lex.europa.eu/legal-content"
HEADERS = {"User-Agent": "boating-licence-study/0.1 (Phase 1 aggregator; personal study tool)"}
WP_API = "https://fr.wikipedia.org/w/api.php"


def _today() -> str:
    return _dt.date.today().isoformat()


def _raw_path(source_id: str, *parts: str) -> str:
    p = os.path.join(RAW_DIR, source_id, *parts)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def _get(url: str, **kw) -> requests.Response:
    """GET with polite retry/backoff on rate-limiting (429) and transient 5xx —
    Wikipedia in particular throttles bursts."""
    headers = {**HEADERS, **kw.pop("headers", {})}
    delay = 2.0
    for attempt in range(5):
        r = requests.get(url, headers=headers, timeout=60, **kw)
        if r.status_code in (429, 503) and attempt < 4:
            wait = float(r.headers.get("Retry-After", delay))
            time.sleep(wait)
            delay *= 2
            continue
        r.raise_for_status()
        return r
    r.raise_for_status()
    return r


# --------------------------------------------------------------------------
# Fedlex (law): resolve the newest XML (+ optional PDF/A) for an ELI, in any of
# the official languages. Swiss law is published officially in FR/DE/IT (and
# sometimes RM); each is a distinct `jolux:language` expression of the same act,
# so only the EU-authority language URI changes — the ELI is language-neutral.
# --------------------------------------------------------------------------

# EU Publications Office authority codes used by Fedlex's jolux:language.
_LANG_URI = {"fr": "FRA", "de": "DEU", "it": "ITA", "rm": "ROH"}

_FEDLEX_Q = """
PREFIX jolux: <http://data.legilux.public.lu/resource/ontology/jolux#>
SELECT ?file ?date WHERE {{
  ?expr jolux:isEmbodiedBy ?manif .
  ?manif jolux:isExemplifiedBy ?file .
  ?expr jolux:language <http://publications.europa.eu/resource/authority/language/{languri}> .
  ?cons jolux:isRealizedBy ?expr .
  ?cons jolux:dateApplicability ?date .
  FILTER(CONTAINS(STR(?file), "{eli}"))
  FILTER(CONTAINS(STR(?file), "/{fmt}/"))
}}
ORDER BY DESC(?date) LIMIT 1
"""


def _resolve_fedlex_file(eli: str, fmt: str, lang: str = "fr") -> tuple[str, str] | None:
    """Return (file_url, consolidation_date) for the newest `lang` `fmt` manifestation."""
    q = _FEDLEX_Q.format(eli=eli, fmt=fmt, languri=_LANG_URI[lang])
    r = _get(SPARQL, params={"query": q},
             headers={**HEADERS, "Accept": "application/sparql-results+json"})
    rows = r.json()["results"]["bindings"]
    if not rows:
        return None
    b = rows[0]
    return b["file"]["value"], b["date"]["value"]


def _fetch_xml_images(cache_key: str, xml_url: str, xml_bytes: bytes) -> dict:
    """Download every distinct image referenced by the act XML. Returns
    {src_ref: {"path": local, "bytes": n}} keyed by the ref used in the XML."""
    from lxml import etree
    AKN = "{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}"
    root = etree.fromstring(xml_bytes)
    base = xml_url.rsplit("/", 1)[0]
    refs = sorted({im.get("src") for im in root.iter(AKN + "img") if im.get("src")})
    out = {}
    for ref in refs:
        url = urllib.parse.urljoin(base + "/", ref)
        try:
            content = _get(url).content
        except requests.HTTPError:
            continue
        local = _raw_path(cache_key, "images", os.path.basename(ref))
        with open(local, "wb") as fh:
            fh.write(content)
        out[ref] = {"path": os.path.relpath(local), "bytes": len(content), "url": url}
    return out


def fetch_fedlex(src: Source, force: bool = False, lang: str = "fr") -> dict:
    """Fetch one act in one language. French keeps the legacy cache layout
    (data/raw/<id>/); other languages live in a per-language subdir
    (data/raw/<id>/<lang>/) so the FR build is untouched."""
    if lang not in _LANG_URI:
        raise ValueError(f"unsupported fedlex language {lang!r}")
    cache_key = src.id if lang == "fr" else os.path.join(src.id, lang)
    manifest_path = _raw_path(cache_key, "manifest.json")
    if os.path.exists(manifest_path) and not force:
        with open(manifest_path, encoding="utf-8") as fh:
            return json.load(fh)

    files: dict[str, str] = {}
    version = ""
    xml = _resolve_fedlex_file(src.eli, "xml", lang)
    if not xml:
        raise RuntimeError(
            f"[{src.id}] no Fedlex {lang.upper()} XML found for ELI {src.eli}")
    xml_url, version = xml
    xml_bytes = _get(xml_url).content
    xml_local = _raw_path(cache_key, "act.xml")
    with open(xml_local, "wb") as fh:
        fh.write(xml_bytes)
    files["xml"] = {"url": xml_url, "path": os.path.relpath(xml_local)}

    # Annex figures: the XML references images relatively ("image/imageN.png").
    # They resolve from the same filestore directory as the XML — pull them so
    # the signalisation theme has its diagrams, named and in article context.
    images = _fetch_xml_images(cache_key, xml_url, xml_bytes)
    if images:
        files["images"] = images

    if src.want_pdf:
        pdf = _resolve_fedlex_file(src.eli, "pdf-a", lang)
        if pdf:
            pdf_url, _ = pdf
            pdf_local = _raw_path(cache_key, "act.pdf")
            with open(pdf_local, "wb") as fh:
                fh.write(_get(pdf_url).content)
            files["pdf"] = {"url": pdf_url, "path": os.path.relpath(pdf_local)}

    manifest = {
        "source_id": src.id, "kind": src.kind, "lang": lang, "retrieved": _today(),
        "legal_version": version, "files": files, "canonical_url": src.url,
    }
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
    return manifest


# --------------------------------------------------------------------------
# gesetze-im-internet.de (German federal law): each ordinance ships as a single
# <slug>/xml.zip — one gii-norm XML plus any bundled annex images. Public domain
# under §5(1) UrhG. The German analogue of the Fedlex path; German law is
# single-language, so there is no per-language manifestation to resolve.
# --------------------------------------------------------------------------

def _gii_version(xml_path: str) -> str:
    """Best-effort 'as-of' for a gii act: the 'Stand' comment if present, else the
    promulgation (Ausfertigung) date — read from the framing header norm."""
    from lxml import etree
    root = etree.parse(xml_path).getroot()
    stand = root.findtext(".//standangabe/standkommentar")
    if stand and stand.strip():
        return re.sub(r"\s+", " ", stand).strip()
    aus = root.findtext(".//ausfertigung-datum")
    return (aus or "").strip()


def fetch_gii(src: Source, force: bool = False, lang: str = "de") -> dict:
    """Fetch one German ordinance. Mirrors fetch_fedlex's cache layout: FR (n/a
    here) would stay flat, other languages live under data/raw/<id>/<lang>/."""
    cache_key = src.id if lang == "fr" else os.path.join(src.id, lang)
    manifest_path = _raw_path(cache_key, "manifest.json")
    if os.path.exists(manifest_path) and not force:
        with open(manifest_path, encoding="utf-8") as fh:
            return json.load(fh)

    slug = src.gii_slug or src.id
    url = f"{GII_BASE}/{slug}/xml.zip"
    zf = zipfile.ZipFile(io.BytesIO(_get(url).content))

    files: dict = {}
    images: dict = {}
    xml_local = ""
    for name in zf.namelist():
        if name.endswith("/"):
            continue
        data = zf.read(name)
        base = os.path.basename(name)
        if base.lower().endswith(".xml"):
            xml_local = _raw_path(cache_key, "act.xml")
            with open(xml_local, "wb") as fh:
                fh.write(data)
            files["xml"] = {"url": url, "path": os.path.relpath(xml_local)}
        else:                                  # bundled annex image, keyed by name
            local = _raw_path(cache_key, "images", base)
            with open(local, "wb") as fh:
                fh.write(data)
            images[base] = {"path": os.path.relpath(local), "bytes": len(data)}
    if not xml_local:
        raise RuntimeError(f"[{src.id}] no XML found in {url}")
    if images:
        files["images"] = images

    manifest = {
        "source_id": src.id, "kind": src.kind, "lang": lang, "retrieved": _today(),
        "legal_version": _gii_version(xml_local), "files": files,
        "canonical_url": src.url,
    }
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
    return manifest


# --------------------------------------------------------------------------
# wetten.overheid.nl / KOOP (Dutch law): the Basis Wetten Bestand publishes every
# consolidated state of an act ("toestand") as XML in an open repository, indexed
# by a per-act manifest.xml whose `_latestItem` names the current state. Dutch law
# carries no copyright at all (Auteurswet art. 11), so this is the cleanest of the
# three law portals. Single-language (Dutch law is enacted in Dutch only), so
# there is no per-language manifestation to resolve — unlike Fedlex.
# --------------------------------------------------------------------------

def _bwb_latest(bwb_id: str) -> tuple[str, str]:
    """(state_path, in-force date) for the newest consolidated state of an act.

    The manifest's ``_latestItem`` is the authoritative pointer — it is what
    wetten.overheid.nl itself serves — so we never guess a date.
    """
    manifest = _get(f"{BWB_BASE}/{bwb_id}/manifest.xml").text
    m = re.search(r'_latestItem="([^"]+)"', manifest)
    if not m:
        raise RuntimeError(f"[{bwb_id}] BWB manifest names no _latestItem")
    item = m.group(1)                       # "<date>_0/xml/<id>_<date>_0.xml"
    date = item.split("_", 1)[0]
    return item, date


# The BPR alone carries 400+ annex figures (every waterway sign, light and sound
# pattern). Sub-kilobyte PNGs are layout glyphs, not plates — the parser filters
# on the same threshold the German one uses.
_BWB_IMG = re.compile(r'<illustratie[^>]*\bnaam="([^"]+)"')


def fetch_bwb(src: Source, force: bool = False, lang: str = "nl") -> dict:
    """Fetch one Dutch act (newest consolidated state) plus its annex figures."""
    cache_key = src.id if lang == "fr" else os.path.join(src.id, lang)
    manifest_path = _raw_path(cache_key, "manifest.json")
    if os.path.exists(manifest_path) and not force:
        with open(manifest_path, encoding="utf-8") as fh:
            return json.load(fh)

    bwb_id = src.bwb_id or src.id
    item, version = _bwb_latest(bwb_id)
    xml_url = f"{BWB_BASE}/{bwb_id}/{item}"
    xml_bytes = _get(xml_url).content
    xml_local = _raw_path(cache_key, "act.xml")
    with open(xml_local, "wb") as fh:
        fh.write(xml_bytes)
    files: dict = {"xml": {"url": xml_url, "path": os.path.relpath(xml_local)}}

    # Figures sit beside the XML in the same state directory.
    img_base = xml_url.rsplit("/", 1)[0] + "/"
    images: dict = {}
    for name in sorted(set(_BWB_IMG.findall(xml_bytes.decode("utf-8", "replace")))):
        try:
            data = _get(urllib.parse.urljoin(img_base, name)).content
        except requests.HTTPError:
            continue
        local = _raw_path(cache_key, "images", os.path.basename(name))
        with open(local, "wb") as fh:
            fh.write(data)
        images[name] = {"path": os.path.relpath(local), "bytes": len(data),
                        "url": urllib.parse.urljoin(img_base, name)}
    if images:
        files["images"] = images

    manifest = {
        "source_id": src.id, "kind": src.kind, "lang": lang, "retrieved": _today(),
        "legal_version": version, "files": files, "canonical_url": src.url,
        "bwb_id": bwb_id,
    }
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
    return manifest


# --------------------------------------------------------------------------
# EUR-Lex (EU law): one act, 24 official-language expressions, same CELEX. Reuse
# is authorised by Commission Decision 2011/833/EU. As with Fedlex we resolve the
# newest *consolidated* expression rather than pinning a date: EUR-Lex numbers a
# consolidation "0<base>-<YYYYMMDD>", and the act's ALL page lists every one.
# --------------------------------------------------------------------------

_CONSOLIDATED = re.compile(r"\b0(\d{4}[LR]\d{4})-(\d{8})\b")


def _eurlex_consolidated(celex: str) -> str:
    """The newest consolidated CELEX for a base CELEX, or "" when the act has
    never been amended (then the base text *is* the text in force)."""
    base = celex.lstrip("3")
    url = f"{EURLEX_BASE}/EN/ALL/?uri=CELEX:{celex}"
    try:
        page = _get(url).text
    except requests.HTTPError:
        return ""
    dates = sorted(d for b, d in _CONSOLIDATED.findall(page) if b == base)
    return f"0{base}-{dates[-1]}" if dates else ""


# A rendition is usable only if it carries the ELI article skeleton the parser
# reads. EUR-Lex does NOT serve the consolidated text with that skeleton in every
# language — for Directive 2013/53/EU it is structured in EN and DE but a plain
# unmarked page in NL and FR — and an unmarked page parses to *zero articles*
# rather than to an error, which is the dangerous kind of failure.
_STRUCTURED = re.compile(rb'class="eli-subdivision"[^>]*id="art_\d+"')


def _eurlex_url(celex: str, lang: str) -> str:
    return f"{EURLEX_BASE}/{lang.upper()}/TXT/HTML/?uri=CELEX:{celex}"


def fetch_eurlex(src: Source, force: bool = False, lang: str = "en") -> dict:
    """Fetch one EU act in one official language.

    Prefers the newest consolidated version — that is the text in force — and
    falls back to the act as published in the Official Journal when EUR-Lex has
    no *structured* consolidated rendition in this language. Which one was taken
    is recorded per unit (``text_status``), never silently swapped.
    """
    cache_key = src.id if lang == "fr" else os.path.join(src.id, lang)
    manifest_path = _raw_path(cache_key, "manifest.json")
    if os.path.exists(manifest_path) and not force:
        with open(manifest_path, encoding="utf-8") as fh:
            return json.load(fh)

    celex = src.celex or src.id
    consolidated = _eurlex_consolidated(celex)
    effective, status = (consolidated, "consolidated") if consolidated else (celex, "as-published")
    url = _eurlex_url(effective, lang)
    body = _get(url).content
    if status == "consolidated" and not _STRUCTURED.search(body):
        effective, status = celex, "as-published"
        url = _eurlex_url(effective, lang)
        body = _get(url).content

    local = _raw_path(cache_key, "act.html")
    with open(local, "wb") as fh:
        fh.write(body)

    manifest = {
        "source_id": src.id, "kind": src.kind, "lang": lang, "retrieved": _today(),
        # The CELEX actually taken IS the legal version; an act with no
        # consolidation reports its base CELEX so the staleness check can diff it.
        "legal_version": effective,
        "text_status": status,
        # Recorded even when unused, so it is visible that a newer consolidation
        # exists in another language and this one is still on the OJ text.
        "latest_consolidated": consolidated,
        "files": {"html": {"url": url, "path": os.path.relpath(local)}},
        "canonical_url": src.url, "celex": celex,
    }
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
    return manifest


# --------------------------------------------------------------------------
# Wikipedia: pull parsed HTML + revision id per page via the MediaWiki API.
# --------------------------------------------------------------------------

def fetch_wikipedia(src: Source, force: bool = False) -> dict:
    manifest_path = _raw_path(src.id, "manifest.json")
    if os.path.exists(manifest_path) and not force:
        with open(manifest_path, encoding="utf-8") as fh:
            return json.load(fh)

    api = f"https://{src.lang}.wikipedia.org/w/api.php"   # language edition
    pages = {}
    for i, title in enumerate(src.titles):
        if i:
            time.sleep(1.0)            # be polite: one page/sec
        r = _get(api, params={
            "action": "parse", "page": title, "prop": "text|revid",
            "format": "json", "redirects": 1, "formatversion": 2,
        })
        data = r.json()
        if "error" in data:
            pages[title] = {"error": data["error"].get("info", "unknown")}
            continue
        p = data["parse"]
        local = _raw_path(src.id, f"page_{p.get('revid', 0)}.html")
        with open(local, "w", encoding="utf-8") as fh:
            fh.write(p["text"])
        pages[title] = {"revid": p.get("revid"), "path": os.path.relpath(local),
                        "real_title": p.get("title", title)}

    manifest = {
        "source_id": src.id, "kind": src.kind, "lang": src.lang,
        "retrieved": _today(),
        "legal_version": "", "pages": pages, "canonical_url": src.url,
    }
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
    return manifest


# --------------------------------------------------------------------------
# Generic HTML: cache the raw page verbatim.
# --------------------------------------------------------------------------

def fetch_html(src: Source, force: bool = False) -> dict:
    manifest_path = _raw_path(src.id, "manifest.json")
    if os.path.exists(manifest_path) and not force:
        with open(manifest_path, encoding="utf-8") as fh:
            return json.load(fh)

    r = _get(src.url)
    local = _raw_path(src.id, "page.html")
    with open(local, "wb") as fh:
        fh.write(r.content)
    manifest = {
        "source_id": src.id, "kind": src.kind, "retrieved": _today(),
        "legal_version": r.headers.get("Last-Modified", ""),
        "files": {"html": {"url": src.url, "path": os.path.relpath(local)}},
        "canonical_url": src.url,
        "final_url": r.url,
    }
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
    return manifest


def fetch_pdf(src: Source, force: bool = False) -> dict:
    """Cache a PDF document verbatim (e.g. the USCG COLREG International Rules).
    Single-language, like the HTML/Wikipedia sources — the file is fetched only
    when the source's own `lang` is requested; its text is segmented at parse time
    (no per-language manifestation to resolve)."""
    manifest_path = _raw_path(src.id, "manifest.json")
    if os.path.exists(manifest_path) and not force:
        with open(manifest_path, encoding="utf-8") as fh:
            return json.load(fh)

    r = _get(src.url)
    local = _raw_path(src.id, "doc.pdf")
    with open(local, "wb") as fh:
        fh.write(r.content)
    manifest = {
        "source_id": src.id, "kind": src.kind, "lang": src.lang,
        "retrieved": _today(),
        "legal_version": r.headers.get("Last-Modified", ""),
        "files": {"pdf": {"url": src.url, "path": os.path.relpath(local),
                          "bytes": len(r.content)}},
        "canonical_url": src.url,
        "final_url": r.url,
    }
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
    return manifest


_DISPATCH = {"fedlex": fetch_fedlex, "gii": fetch_gii, "bwb": fetch_bwb,
             "eurlex": fetch_eurlex,
             "wikipedia": fetch_wikipedia, "html": fetch_html, "pdf": fetch_pdf}
# Law kinds: one act, fetched (and cached) as a per-language manifestation. The
# set is about *layout*, not about how many languages exist — `gii` and `bwb` each
# have exactly one (German, Dutch), `fedlex` four and `eurlex` twenty-four; all
# four keep their raw cache under data/raw/<id>/<lang>/, which is the layout
# parse._manifest reads back.
_PER_LANG_KINDS = {"fedlex", "gii", "bwb", "eurlex"}


def fetch_source(src: Source, force: bool = False) -> dict:
    return _DISPATCH[src.kind](src, force=force)


def fetch_all(sources: list[Source] | None = None, force: bool = False) -> dict[str, dict]:
    out = {}
    for src in (sources or SOURCES):
        out[src.id] = fetch_source(src, force=force)
    return out


def fetch_fedlex_langs(langs: list[str], sources: list[Source] | None = None,
                       force: bool = False) -> dict[str, dict]:
    """Fetch the law (fedlex) sources in additional official languages (de/it).
    Keyed '<id>/<lang>'."""
    out = {}
    for src in (sources or SOURCES):
        if src.kind != "fedlex":
            continue
        for lang in langs:
            out[f"{src.id}/{lang}"] = fetch_fedlex(src, force=force, lang=lang)
    return out


def fetch_for_langs(langs: list[str], sources: list[Source] | None = None,
                    force: bool = False) -> dict[str, dict]:
    """Fetch every source needed for the requested content languages. Law
    (fedlex) acts are fetched once per language (same act, different manifestation);
    language-specific sources (Wikipedia/HTML) are fetched only when their own
    `lang` is requested. Keyed '<id>' (fr law / lang-specific source) or
    '<id>/<lang>' (non-fr law)."""
    out = {}
    for src in (sources or SOURCES):
        if src.kind in _PER_LANG_KINDS:
            for lang in langs:
                key = src.id if lang == "fr" else f"{src.id}/{lang}"
                out[key] = _DISPATCH[src.kind](src, force=force, lang=lang)
        elif src.lang in langs:
            out[src.id] = fetch_source(src, force=force)
    return out
