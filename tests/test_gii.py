"""Tests for the gesetze-im-internet.de law parser (`src/parsers/gii.py`).

Offline: a tiny gii-norm fixture XML (the framing header norm + two provisions)
is parsed and the resulting KnowledgeUnits are checked — the header norm is
skipped, each provision becomes one article unit with the law abbreviation in its
ref, and the German tagger classifies it. No network.

Run with `python tests/test_gii.py`.
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.parsers import gii                              # noqa: E402
from src.sources import Source                           # noqa: E402

# Minimal gii-norm document: <dokumente> with a header norm (no <enbez>) and two
# real provisions. Mirrors the structure of a real <slug>/xml.zip act.xml.
_FIXTURE = """<?xml version="1.0" encoding="UTF-8"?>
<dokumente>
  <norm builddate="20250101000000" doknr="HEADER">
    <metadaten>
      <jurabk>TestO</jurabk>
      <kurzue>Test-Ordnung</kurzue>
      <langue>Verordnung zum Test</langue>
      <ausfertigung-datum>2017-05-03</ausfertigung-datum>
    </metadaten>
    <textdaten><fussnoten><Content><P>(+++ Textnachweis +++)</P></Content></fussnoten></textdaten>
  </norm>
  <norm doknr="N1">
    <metadaten><jurabk>TestO</jurabk><enbez>§ 5</enbez>
      <titel format="XML">Ausweichregeln</titel></metadaten>
    <textdaten><text format="XML"><Content><P>Fahrzeuge mussen einander ausweichen; Vorfahrt hat das Fahrzeug rechts.</P></Content></text></textdaten>
  </norm>
  <norm doknr="N2">
    <metadaten><jurabk>TestO</jurabk><enbez>&#167; 2</enbez>
      <titel format="XML">Begriffsbestimmungen</titel></metadaten>
    <textdaten><text format="XML"><Content><P>Im Sinne dieser Verordnung sind Sportboote Freizeitfahrzeuge.</P></Content></text></textdaten>
  </norm>
</dokumente>
"""

_SRC = Source(id="testo", kind="gii", lang="de", gii_slug="testo",
              name="Test-Ordnung (TestO)",
              url="https://example.invalid/testo/",
              default_theme="verkehrsregeln", licence="PD test")


def _parse_fixture():
    with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False,
                                     encoding="utf-8") as fh:
        fh.write(_FIXTURE)
        path = fh.name
    # gii.parse joins the manifest path under repo-root; an absolute path makes
    # os.path.join return it unchanged, so the fixture resolves directly.
    manifest = {"files": {"xml": {"path": path}}, "retrieved": "2026-05-30",
                "lang": "de", "legal_version": "2017-05-03"}
    try:
        return gii.parse(_SRC, manifest)
    finally:
        os.unlink(path)


def test_header_norm_skipped_and_provisions_parsed():
    units = _parse_fixture()
    assert len(units) == 2, "header norm (no enbez) must be skipped"
    refs = {u.ref for u in units}
    assert refs == {"TestO § 5", "TestO § 2"}            # abbrev from jurabk
    assert all(u.kind == "article" and u.lang == "de" for u in units)
    assert all(u.source_id == "testo" and u.licence == "PD test" for u in units)


def test_provisions_get_german_themes():
    by_ref = {u.ref: u for u in _parse_fixture()}
    assert by_ref["TestO § 5"].theme == "verkehrsregeln"     # Ausweichen/Vorfahrt
    assert by_ref["TestO § 2"].theme == "definitionen"       # Begriffsbestimmungen
    assert "ausweichen" in by_ref["TestO § 5"].text.lower()


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"\n{len(tests)} tests passed")
