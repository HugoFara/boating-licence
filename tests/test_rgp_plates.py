"""Tests for the RGP plate extractor (src/fr/rgp_plates.py).

The plates live in a Journal officiel PDF that has to be placed by hand, so the
extraction tests skip when it is absent — the same shape as the KB-dependent tests.
What can always be checked is that the module refuses clearly rather than half-
working, and that its page-finding logic keys off the annexes' own headings.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.fr import rgp_plates                                       # noqa: E402


def test_missing_pdf_fails_loudly_with_the_way_to_get_it():
    """A silent empty run would look like "the JO has no plates". It must instead
    say which file is missing, where it comes from, and where to put it."""
    if rgp_plates.have_pdf():
        print("    (skipped: the JO PDF is present)")
        return
    try:
        rgp_plates.extract()
        assert False, "expected SystemExit when the JO PDF is absent"
    except SystemExit as exc:
        msg = str(exc)
        assert rgp_plates.PDF in msg
        assert rgp_plates.JO_URL in msg, "the message must say where to get it"


def test_pages_are_found_by_heading_not_hardcoded():
    """The JO's pagination (14632–14723) is not the PDF's, so the annexes must be
    located by the text they open with. Fake a document to prove nothing is keyed to
    a page number."""
    class _Page:
        def __init__(self, text): self._t = text
        def get_text(self): return self._t

    class _Doc:
        def __init__(self, texts): self._p = [_Page(t) for t in texts]
        page_count = property(lambda self: len(self._p))
        def __getitem__(self, i): return self._p[i]

    doc = _Doc([
        "sommaire du journal officiel",
        "ANNEXE 3  Signalisation visuelle des bateaux",
        "suite des croquis",
        "ANNEXE 5  Signaux servant à régler la navigation sur la voie",
        "suite",
        "ANNEXE 8  Balisage des voies de navigation intérieure des lacs",
    ])
    pages = rgp_plates.annex_pages(doc)
    assert pages["annexe-3"] == [1, 2]
    assert pages["annexe-5"] == [3, 4]
    assert pages["annexe-8"] == [5]
    assert 0 not in sum(pages.values(), []), "the summary page is not an annexe"


def test_the_citation_matches_what_the_law_says():
    """The module's constants are the ones annexe 5 itself cites; if they drift the
    extractor would be pulling plates from the wrong issue."""
    assert rgp_plates.JO_PAGES == (14632, 14723)
    assert rgp_plates.JO_TEXTE == 54
    assert "2013" in rgp_plates.JO_ISSUE and "Etalab" in rgp_plates.LICENCE


def test_extract_is_deterministic_when_the_pdf_is_there():
    if not rgp_plates.have_pdf():
        print("    (skipped: data/raw/rgp_jo/ has no JO PDF)")
        return
    first = rgp_plates.extract()
    assert first["plates"] > 0, "the annexe pages carry no images — wrong PDF?"
    again = rgp_plates.extract()
    assert again["written"] == 0, "a re-run rewrote files; extraction is not stable"
    assert again["plates"] == first["plates"]


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
