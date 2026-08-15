"""Tests for the RGP plate extractor (src/fr/rgp_plates.py).

The plates come out of a Journal officiel PDF that has to be placed by hand, so the
tests that need it skip when it is absent. What is always checked: the module refuses
loudly rather than half-working, the sign codes it reads are normalised the way the
JO prints them, and — the one that matters most — a missing plate is *reported*
rather than silently looking like a sign the annexe never had.
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


def test_sign_codes_are_normalised_the_way_the_jo_prints_them():
    """OCR routinely drops the dot after the letter ("A3" for "A.3"). Both spellings
    must land on one canonical code, or the same sign is filed twice."""
    ok = {"A.3": "A.3", "A3": "A.3", "A.4.1": "A.4.1", "A4.1": "A.4.1",
          "E.5.10": "E.5.10", "B.11:": "B.11", "C.2.": "C.2"}
    for raw, want in ok.items():
        m = rgp_plates._CODE.match(raw)
        assert m, f"{raw!r} should read as a sign code"
        assert f"{m.group(1)}.{m.group(2)}" == want, raw
    for raw in ("Annexe", "4241-53-12", "F.1", "29", "A."):
        assert not rgp_plates._CODE.match(raw), f"{raw!r} is not a sign code"


def test_gaps_are_reported_not_swallowed():
    """A plate OCR failed to find must show up as a hole in the numbering. The
    dangerous failure here is the invisible one — a missing sign looks exactly like a
    sign the annexe does not define."""
    man = {"plates": [{"code": c} for c in
                      ("A.1", "A.2", "A.4", "B.1", "B.2", "E.5.1")]}
    g = rgp_plates.gaps(man)
    assert g["A"] == ["A.3"], g
    assert "B" not in g, "B.1 and B.2 are contiguous"
    # a family whose numbering is complete produces no entry at all
    assert rgp_plates.gaps({"plates": [{"code": "C.1"}, {"code": "C.2"}]}) == {}


def test_the_citation_matches_what_the_law_says():
    """The module's constants are the ones annexe 5 itself cites; if they drift the
    extractor would be pulling plates from the wrong issue."""
    assert rgp_plates.JO_PAGES == (14632, 14723)
    assert rgp_plates.JO_TEXTE == 54
    assert "2013" in rgp_plates.JO_ISSUE and "Etalab" in rgp_plates.LICENCE


def test_manifest_pairs_every_plate_with_a_caption():
    """The code→plate pairing is read off the page, and the caption printed beside it
    is kept so a human can check that pairing at a glance. A plate with no caption
    cannot be verified, so it must not be in the index."""
    man = rgp_plates.load_manifest()
    plates = man.get("plates", [])
    if not plates:
        print("    (skipped: no plates extracted yet)")
        return
    assert man["licence"].startswith("Licence Ouverte")
    for p in plates:
        assert rgp_plates._CODE.match(p["code"].replace(".", "", 0)), p["code"]
        assert p["caption"].strip(), f"{p['code']}: no caption to check against"
        assert p["path"].startswith("data/assets/rgp/"), p["path"]
        assert p["size"][0] > 20 and p["size"][1] > 20, f"{p['code']}: crop too small"


def test_extract_is_deterministic_when_the_pdf_is_there():
    if not rgp_plates.have_pdf():
        print("    (skipped: data/raw/rgp_jo/ has no JO PDF)")
        return
    again = rgp_plates.extract()
    assert again["plates"] > 0, "the annexe pages carry no plates — wrong PDF?"
    assert again["written"] == 0, "a re-run rewrote files; extraction is not stable"


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
