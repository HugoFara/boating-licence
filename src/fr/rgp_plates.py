"""Extract the RGP's signal plates from the Journal officiel PDF.

Why this exists
---------------
Every other French source in this repo is ingested from text. The RGP's figures are
not *in* the text: annexe 3 (vessel signals), annexe 5 (waterway signs) and annexe 8
(buoyage) each say, where a plate should be,

    « Vous pouvez consulter les clichés dans le JO n° 200 du 29/08/2013
      texte numéro 54 … pageDebut=14632&pageFin=14723 »

and stop. The LEGI open data carries that prose and nothing else, so the 34 French
inland sign questions currently assert appearances ("panneau rectangulaire à bord
rouge barré d'une bande blanche horizontale") against a citation the repo cannot
check, and no sign can be illustrated. The plates are the missing 92 pages.

Getting the file
----------------
The PDF is a French official act — freely reusable under the Licence Ouverte /
Etalab, like every other source here. It is **not** in DILA's open data (their JORF
dataset is XML text; there is no PDF dataset), and Légifrance's own download
endpoint is JavaScript-gated: every direct request returns the portal page. So the
file is placed by hand, exactly as the 1.2 GB LEGI dump already is:

    1. open  https://www.legifrance.gouv.fr/jorf/jo/2013/8/29/0200
    2. download the issue PDF (JO n° 200 du 29 août 2013)
    3. save it as  data/raw/rgp_jo/jo_20130829_0200.pdf

then run::

    python -m src.fr.rgp_plates extract

What it does
------------
Locates the annexe pages by their own headings rather than by hardcoded page
numbers — the JO pagination (14632–14723) is not the PDF's — and writes each
embedded plate to ``data/assets/rgp/``. Output is deterministic: the same PDF gives
the same files, named by the page and the order the plate appears on it.

It deliberately does **not** guess which plate is which sign. A figure attached to
the wrong sign code teaches the wrong board, which is worse than none — the same
rule that governs every drawing in ``src/questions/diagrams.py``. Mapping plate →
sign code is a separate, reviewed step against the annex's own section order.
"""

from __future__ import annotations

import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_DIR = os.path.join(ROOT, "data", "raw", "rgp_jo")
PDF = os.path.join(RAW_DIR, "jo_20130829_0200.pdf")
ASSET_DIR = os.path.join(ROOT, "data", "assets", "rgp")

# The issue and the text within it, as annexe 5 itself cites them.
JO_ISSUE = "JO n° 200 du 29 août 2013"
JO_TEXTE = 54
JO_PAGES = (14632, 14723)
JO_URL = "https://www.legifrance.gouv.fr/jorf/jo/2013/8/29/0200"
LICENCE = ("Licence Ouverte / Open Licence 2.0 (Etalab) — Journal officiel de la "
           "République française (DILA), librement réutilisable.")

_MISSING = f"""missing the Journal officiel PDF: {PDF}

The RGP keeps its signal plates in the JO, not in the law text, and neither DILA's
open data nor Légifrance's download endpoint will serve the file to a script. Fetch
it once by hand:

  1. open   {JO_URL}
  2. download the issue PDF ({JO_ISSUE})
  3. save it as  data/raw/rgp_jo/jo_20130829_0200.pdf

then re-run: python -m src.fr.rgp_plates extract"""

# Headings that open the plate-bearing annexes, matched on the page text. Accents and
# spacing in the JO are inconsistent, so match loosely and case-insensitively.
_ANNEX_HEADINGS: list[tuple[str, str]] = [
    ("annexe-3", r"signalisation\s+visuelle\s+des\s+bateaux"),
    ("annexe-5", r"signaux\s+servant\s+.\s+r.gler\s+la\s+navigation"),
    ("annexe-8", r"balisage\s+des\s+voies\s+de\s+navigation\s+int.rieure"),
]


def have_pdf() -> bool:
    return os.path.exists(PDF)


def _open():
    if not have_pdf():
        raise SystemExit(_MISSING)
    try:
        import fitz                       # PyMuPDF, already a dependency
    except ImportError as exc:            # pragma: no cover
        raise SystemExit("PyMuPDF is required: pip install -r requirements.txt") from exc
    return fitz.open(PDF)


def annex_pages(doc) -> dict[str, list[int]]:
    """0-based PDF page indices per annexe, found by heading.

    The JO's own pagination (14632–14723) is not the PDF's, and an issue PDF may or
    may not start at page 1 of the issue, so nothing is hardcoded: each annexe is
    located by the heading it opens with, and runs until the next one starts."""
    starts: list[tuple[int, str]] = []
    for i in range(doc.page_count):
        text = " ".join(doc[i].get_text().split()).lower()
        for name, pat in _ANNEX_HEADINGS:
            if re.search(pat, text) and name not in {n for _, n in starts}:
                starts.append((i, name))
    starts.sort()
    out: dict[str, list[int]] = {}
    for k, (page, name) in enumerate(starts):
        end = starts[k + 1][0] if k + 1 < len(starts) else doc.page_count
        out[name] = list(range(page, end))
    return out


def extract() -> dict:
    """Write every embedded plate of the annexe pages to data/assets/rgp/.

    Deterministic: names are `<annexe>-p<page>-<n>.png`, so the same PDF always
    produces the same files and a re-run is a no-op."""
    doc = _open()
    os.makedirs(ASSET_DIR, exist_ok=True)
    pages = annex_pages(doc)
    if not pages:
        raise SystemExit(
            f"no annexe headings found in {PDF} — is this really {JO_ISSUE}?")
    written, seen = 0, 0
    manifest: list[dict] = []
    for annexe, idxs in sorted(pages.items()):
        for page in idxs:
            for n, img in enumerate(doc[page].get_images(full=True)):
                seen += 1
                name = f"{annexe}-p{page:04d}-{n:02d}.png"
                dst = os.path.join(ASSET_DIR, name)
                pix = doc.extract_image(img[0])
                blob = pix["image"]
                old = open(dst, "rb").read() if os.path.exists(dst) else None
                if old != blob:
                    with open(dst, "wb") as fh:
                        fh.write(blob)
                    written += 1
                manifest.append({"annexe": annexe, "page": page, "index": n,
                                 "path": os.path.relpath(dst, ROOT),
                                 "ext": pix.get("ext", "png")})
    doc.close()
    return {"annexes": {k: len(v) for k, v in sorted(pages.items())},
            "plates": seen, "written": written, "manifest": manifest}


def main(argv: list[str] | None = None) -> None:
    import sys
    args = argv if argv is not None else sys.argv[1:]
    cmd = args[0] if args else "extract"
    if cmd != "extract":
        raise SystemExit("usage: python -m src.fr.rgp_plates extract")
    st = extract()
    print(f"✓ {st['plates']} plates ({st['written']} changed) → "
          f"{os.path.relpath(ASSET_DIR, ROOT)}/")
    for annexe, n in st["annexes"].items():
        print(f"  {annexe}: {n} pages")
    print("  next: map plates to sign codes (reviewed), then attach as official "
          "figures — never guessed")


if __name__ == "__main__":       # pragma: no cover
    main()
