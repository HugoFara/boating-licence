"""Extract the RGP's signal plates from the Journal officiel PDF.

Why this exists
---------------
Every other French source in this repo is ingested from text. The RGP's figures are
not *in* the text: annexes 3, 5 and 8 each say, where a plate should be,

    « Vous pouvez consulter les clichés dans le JO n° 200 du 29/08/2013
      texte numéro 54 … pageDebut=14632&pageFin=14723 »

and stop. LEGI carries that prose and nothing else, which is why 34 French inland
questions assert appearances ("panneau rectangulaire à bord rouge barré d'une bande
blanche horizontale") against a citation the repo could not check, and why no French
sign could be illustrated.

Getting the file
----------------
The PDF is a French official act — freely reusable under the Licence Ouverte /
Etalab, like every other source here. It is **not** in DILA's open data (their JORF
dataset is XML text; there is no PDF dataset), and Légifrance's download endpoint is
JavaScript-gated: with a full browser session, the right Referer and
``Accept: application/pdf`` it still answers with the portal page. So the file is
placed by hand, exactly as the 1.2 GB LEGI dump already is:

    1. open  https://www.legifrance.gouv.fr/jorf/jo/2013/8/29/0200
    2. download the issue PDF (JO n° 200 du 29 août 2013)
    3. save it as  data/raw/rgp_jo/jo_20130829_0200.pdf

then run::

    python -m src.fr.rgp_plates extract

How it reads the annexes
------------------------
The annexes are typeset as **page images** — 72 pages carrying one scanned image
each and no text layer at all, so nothing can be located by searching the PDF's
text, and the plates are not separable embedded images either. Both are read by OCR
(tesseract, French), which is only safe because the JO's layout is rigidly regular:

* each annexe opens with a banner naming it, so the page ranges are read off the
  document rather than hardcoded — the JO's own pagination (14632–14723) is not the
  PDF's, and this issue puts annexe 5 on PDF pages 180–197;
* inside annexe 5 every entry is one row: the **sign code** (A.1, B.2, C.5.1…) in a
  left column at a fixed indent, its caption beside it, and the **plate** alone in a
  right column. So a plate is cropped from the band between one code and the next.

That regularity is what lets the code→plate mapping be *read* instead of guessed. A
figure filed under the wrong sign code would teach the wrong board, which is worse
than shipping none — the rule that governs every figure in this project. So each
plate is saved under the code the document prints next to it, together with the
caption printed beside it, and a row whose caption could not be read is **dropped**:
without it the pairing cannot be checked, and an unverifiable figure is exactly what
this project does not ship. ``gaps()`` then reports the holes, because a silently
missing plate looks identical to a sign the annexe never defined.

What the plates do and do not establish
---------------------------------------
The JO prints these annexes in **black and white** — the extracted plates contain no
coloured pixel at all. They therefore settle a sign's *shape, layout and pictogram*
and say nothing about its colour. The French questions that assert "panneau
rectangulaire à bord **rouge**" are still, on that one point, unsourced by anything
in this repo: the RGP leaves sign colours to the plates, and the plates are
monochrome. Worth knowing before anyone treats these as a colour reference.
"""

from __future__ import annotations

import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_DIR = os.path.join(ROOT, "data", "raw", "rgp_jo")
PDF = os.path.join(RAW_DIR, "jo_20130829_0200.pdf")
ASSET_DIR = os.path.join(ROOT, "data", "assets", "rgp")
MANIFEST = os.path.join(ROOT, "src", "fr", "rgp_plates.json")   # committed index

# The issue and the text within it, as annexe 5 itself cites them.
JO_ISSUE = "JO n° 200 du 29 août 2013"
JO_TEXTE = 54
JO_PAGES = (14632, 14723)
JO_URL = "https://www.legifrance.gouv.fr/jorf/jo/2013/8/29/0200"
LICENCE = ("Licence Ouverte / Open Licence 2.0 (Etalab) — Journal officiel de la "
           "République française (DILA), librement réutilisable.")
SOURCE_NAME = f"Journal officiel de la République française, {JO_ISSUE}, texte {JO_TEXTE}"

DPI = 300                      # the codes are small print; 200 loses some of them
# The sign code sits in a narrow left column. Reading it from a dedicated crop of
# that column, in single-block mode, is markedly more reliable than picking it out
# of a whole-page pass: at page scale tesseract silently dropped ten codes,
# including A.1 (the general prohibition) and E.5 — both of which the French
# questions ask about.
_CODE_COL = (0.05, 0.26)
_LANG = "fra"

_MISSING = f"""missing the Journal officiel PDF: {PDF}

The RGP keeps its signal plates in the JO, not in the law text, and neither DILA's
open data nor Légifrance's download endpoint will serve the file to a script. Fetch
it once by hand:

  1. open   {JO_URL}
  2. download the issue PDF ({JO_ISSUE})
  3. save it as  data/raw/rgp_jo/jo_20130829_0200.pdf

then re-run: python -m src.fr.rgp_plates extract"""

# Annexe banners, as OCR reads them off the page image.
_ANNEXES = {
    "annexe-3": r"annexe\s*3\s*[àa]\s*l.?article",     # signalisation visuelle des bateaux
    "annexe-5": r"annexe\s*5\s*[àa]\s*l.?article",     # signaux de la voie navigable
    "annexe-8": r"annexe\s*8\s*[àa]\s*l.?article",     # balisage
}
_ANY_ANNEXE = r"annexe\s*(\d+)\s*[àa]\s*l.?article"

# A sign code as the JO prints it. OCR frequently loses the dot after the letter
# ("A3" for "A.3"), so it is optional and the code is normalised on the way out.
_CODE = re.compile(r"^([A-E])\.?(\d+(?:\.\d+)?)[.:]?$")


def have_pdf() -> bool:
    return os.path.exists(PDF)


def _fitz():
    try:
        import fitz                       # PyMuPDF, already a dependency
    except ImportError as exc:            # pragma: no cover
        raise SystemExit("PyMuPDF is required: pip install -r requirements.txt") from exc
    return fitz


def _open():
    if not have_pdf():
        raise SystemExit(_MISSING)
    return _fitz().open(PDF)


def _page_image(doc, page: int):
    import io
    from PIL import Image
    pm = doc[page].get_pixmap(dpi=DPI)
    return Image.open(io.BytesIO(pm.tobytes("png")))


def plate_pages(doc) -> list[int]:
    """Pages that are a scanned image with no text layer — the annexes."""
    return [i for i in range(doc.page_count)
            if len(doc[i].get_images(full=True)) == 1
            and len(" ".join(doc[i].get_text().split())) < 200]


def annex_pages(doc, pages: list[int] | None = None) -> dict[str, list[int]]:
    """{annexe: [pdf page indices]}, read off each page's own banner by OCR.

    Nothing is keyed to a page number: the JO's pagination is not the PDF's, and an
    issue PDF need not start at issue page 1."""
    import pytesseract
    pages = plate_pages(doc) if pages is None else pages
    starts: list[tuple[int, str]] = []
    for i in pages:
        im = _page_image(doc, i)
        band = im.crop((0, int(im.height * 0.05), im.width, int(im.height * 0.16)))
        head = " ".join(pytesseract.image_to_string(band, lang=_LANG).split()).lower()
        m = re.search(_ANY_ANNEXE, head)
        if m:
            starts.append((i, f"annexe-{m.group(1)}"))
    out: dict[str, list[int]] = {}
    for k, (page, name) in enumerate(starts):
        end = starts[k + 1][0] if k + 1 < len(starts) else (pages[-1] + 1)
        if name in _ANNEXES:
            out[name] = list(range(page, end))
    return out


def _codes(im) -> list[tuple[int, str]]:
    """[(y, code)] read from the left column alone, in single-block mode."""
    import pytesseract
    W, H = im.size
    strip = im.crop((int(W * _CODE_COL[0]), 0, int(W * _CODE_COL[1]), H))
    d = pytesseract.image_to_data(strip, lang=_LANG, config="--psm 6",
                                  output_type=pytesseract.Output.DICT)
    out: dict[int, str] = {}
    for i, txt in enumerate(d["text"]):
        m = _CODE.match((txt or "").strip())
        if m:
            out[d["top"][i]] = f"{m.group(1)}.{m.group(2)}"
    return sorted(out.items())


def _rows(im, data, W: int, H: int) -> list[tuple[str, str, int, int]]:
    """(code, caption, y_top, y_bottom) for every sign entry on the page."""
    codes = _codes(im)
    rows = []
    for k, (y, code) in enumerate(codes):
        words = [(data["left"][j], data["text"][j]) for j in range(len(data["text"]))
                 if (data["text"][j] or "").strip() and abs(data["top"][j] - y) < 14
                 and 0.20 * W < data["left"][j] < 0.62 * W]
        caption = " ".join(t for _, t in sorted(words))
        y2 = codes[k + 1][0] - 20 if k + 1 < len(codes) else H - 60
        rows.append((code, caption, max(0, y - 25), min(H, y2)))
    return rows


def _crop_plate(im, y1: int, y2: int):
    """The plate alone, taken from the right of the gutter that separates it from the
    caption.

    The gutter is found per row, not per page: a long caption reaches further right
    than a short one, and a fixed split leaves stray words glued to the plate. But a
    tall entry — A.1 carries three groups of plates with "soit panneaux / soit feux
    rouges / soit pavillons rouges" written between them — can have its widest blank
    column run land to the *right* of every plate, which would crop away the picture
    entirely. So the gutter is a first guess, and a plain column split is the
    fallback; the first candidate that yields a real picture wins."""
    import numpy as np
    W, _H = im.size
    band = im.crop((0, y1, W, y2))
    dark = (np.array(band.convert("L")) < 215).sum(axis=0)
    lo, hi = int(W * 0.35), int(W * 0.92)
    best_run, best_end, run = 0, lo, 0
    for x in range(lo, hi):
        if dark[x] <= 1:
            run += 1
            if run > best_run:
                best_run, best_end = run, x
        else:
            run = 0
    candidates = []
    if best_run >= 12:
        candidates.append(best_end + 1)
    candidates.append(int(W * 0.62))
    for left in candidates:
        plate = band.crop((left, 0, W, y2 - y1))
        arr = np.array(plate.convert("L")) < 215
        if not arr.any():
            continue
        ys, xs = np.where(arr)
        out = plate.crop((max(0, xs.min() - 6), max(0, ys.min() - 6),
                          min(plate.width, xs.max() + 7),
                          min(plate.height, ys.max() + 7)))
        if out.width >= 40 and out.height >= 40:
            return out
    return None


def extract(annexes: tuple[str, ...] = ("annexe-5",)) -> dict:
    """Slice each sign's plate out of the annexe pages, named by its own code.

    Deterministic: the same PDF gives the same files, so a re-run writes nothing."""
    import pytesseract
    doc = _open()
    pages = plate_pages(doc)
    if not pages:
        raise SystemExit(f"no page-image annexes in {PDF} — is this really {JO_ISSUE}?")
    found = annex_pages(doc, pages)
    missing = [a for a in annexes if a not in found]
    if missing:
        raise SystemExit(f"annexe banner(s) not found: {missing} (saw {sorted(found)})")
    os.makedirs(ASSET_DIR, exist_ok=True)
    manifest: list[dict] = []
    written = dupes = uncaptioned = 0
    seen: set[str] = set()
    for annexe in annexes:
        for page in found[annexe]:
            im = _page_image(doc, page)
            W, H = im.size
            data = pytesseract.image_to_data(
                im, lang=_LANG, output_type=pytesseract.Output.DICT)
            for code, caption, y1, y2 in _rows(im, data, W, H):
                plate = _crop_plate(im, y1, y2)
                if plate is None:
                    continue
                if not caption.strip():
                    # The caption is how a human checks that this plate really is
                    # this code. Without one the pairing cannot be verified, and an
                    # unverifiable figure is precisely what this project does not
                    # ship — so it is dropped and counted, never quietly indexed.
                    uncaptioned += 1
                    continue
                if code in seen:          # a code printed twice = an OCR mis-read
                    dupes += 1
                    continue
                seen.add(code)
                name = f"{annexe}-{code}.png"
                dst = os.path.join(ASSET_DIR, name)
                import io as _io
                buf = _io.BytesIO(); plate.save(buf, "PNG")
                blob = buf.getvalue()
                old = open(dst, "rb").read() if os.path.exists(dst) else None
                if old != blob:
                    with open(dst, "wb") as fh:
                        fh.write(blob)
                    written += 1
                manifest.append({
                    "annexe": annexe, "code": code, "caption": caption,
                    "page": page, "size": list(plate.size),
                    "path": os.path.relpath(dst, ROOT).replace(os.sep, "/"),
                })
    doc.close()
    manifest.sort(key=lambda m: (m["annexe"], m["code"]))
    with open(MANIFEST, "w", encoding="utf-8") as fh:
        json.dump({"source": SOURCE_NAME, "url": JO_URL, "licence": LICENCE,
                   "jo_pages": list(JO_PAGES), "plates": manifest},
                  fh, ensure_ascii=False, indent=2)
    return {"annexes": {a: len(found[a]) for a in annexes},
            "plates": len(manifest), "written": written, "duplicate_codes": dupes,
            "uncaptioned": uncaptioned}


def gaps(manifest: dict | None = None) -> dict[str, list[str]]:
    """Arithmetic holes in each family's numbering, e.g. A.1 absent between A.2's
    family start and A.20.

    OCR on a 2013 scan is not perfect, and a *silently* missing plate is the
    dangerous kind: it looks like the annexe simply has no such sign. Reporting the
    holes turns an invisible gap into a checkable list, and nothing is attached to a
    question until its pairing has been eyeballed against the caption."""
    man = manifest or load_manifest()
    have: dict[str, set[int]] = {}
    for p in man.get("plates", []):
        fam, _, rest = p["code"].partition(".")
        head = rest.split(".")[0]
        if head.isdigit():
            have.setdefault(fam, set()).add(int(head))
    out: dict[str, list[str]] = {}
    for fam, nums in sorted(have.items()):
        miss = [f"{fam}.{n}" for n in range(1, max(nums) + 1) if n not in nums]
        if miss:
            out[fam] = miss
    return out


def load_manifest() -> dict:
    """The committed plate index (code → file + caption), or an empty one."""
    if not os.path.exists(MANIFEST):
        return {"plates": []}
    with open(MANIFEST, encoding="utf-8") as fh:
        return json.load(fh)


def main(argv: list[str] | None = None) -> None:
    import sys
    args = argv if argv is not None else sys.argv[1:]
    cmd = args[0] if args else "extract"
    if cmd not in ("extract", "list", "gaps"):
        raise SystemExit("usage: python -m src.fr.rgp_plates [extract|list|gaps]")
    if cmd == "gaps":
        g = gaps()
        for fam, miss in g.items():
            print(f"  {fam}: {len(miss)} not extracted — {' '.join(miss)}")
        print("no gaps" if not g else
              f"{sum(len(v) for v in g.values())} codes to re-check by hand")
        return
    if cmd == "list":
        man = load_manifest()
        for p in man.get("plates", []):
            print(f"  {p['code']:8s} p{p['page']:>3}  {p['caption'][:78]}")
        print(f"{len(man.get('plates', []))} plates")
        return
    want = tuple(a for a in args[1:] if a.startswith("annexe-")) or ("annexe-5",)
    st = extract(want)
    print(f"✓ {st['plates']} plates ({st['written']} changed) → "
          f"{os.path.relpath(ASSET_DIR, ROOT)}/")
    for annexe, n in st["annexes"].items():
        print(f"  {annexe}: {n} pages")
    if st["uncaptioned"]:
        print(f"  ⚠ {st['uncaptioned']} plate(s) dropped: no caption was read beside "
              f"them, so the code→plate pairing could not be verified")
    if st["duplicate_codes"]:
        print(f"  ⚠ {st['duplicate_codes']} row(s) skipped: a code appeared twice "
              f"(OCR mis-read) — check with `list` before attaching any of them")
    print(f"  index: {os.path.relpath(MANIFEST, ROOT)}")
    g = gaps()
    if g:
        print(f"  ⚠ {sum(len(v) for v in g.values())} codes not extracted "
              f"(OCR on a 2013 scan) — `python -m src.fr.rgp_plates gaps` to list "
              f"them; none of this is attached to a question yet")


if __name__ == "__main__":       # pragma: no cover
    main()
