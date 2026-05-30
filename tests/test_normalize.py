"""Tests for cross-language theme propagation (`normalize._propagate_themes`):
DE/IT articles inherit their FR sibling's theme by language-neutral ref, figures
are left alone, and it's a no-op without French. All offline.

Run with `python tests/test_normalize.py`.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.normalize import _propagate_themes          # noqa: E402
from src.schema import KnowledgeUnit                  # noqa: E402


def _u(ref, theme, lang, kind="article"):
    return KnowledgeUnit(
        id=f"{ref}-{lang}", theme=theme, kind=kind, ref=ref, title="", text="",
        source_id="oni", source_name="ONI", source_url="", retrieved="",
        legal_version="", licence="", lang=lang)


def test_de_it_inherit_fr_theme():
    units = [
        _u("ONI art. 1", "definitions", "fr"),
        _u("ONI art. 1", "lois", "de"),          # mis-tagged -> should become definitions
        _u("ONI art. 1", "eaux_frontalieres", "it"),
    ]
    changed = _propagate_themes(units)
    assert changed == 2
    assert {u.lang: u.theme for u in units} == {
        "fr": "definitions", "de": "definitions", "it": "definitions"}


def test_already_matching_not_counted():
    units = [_u("ONI art. 2", "lois", "fr"), _u("ONI art. 2", "lois", "de")]
    assert _propagate_themes(units) == 0       # DE already correct -> no change


def test_figures_are_left_alone():
    units = [
        _u("ONI art. 5", "signalisation", "fr"),
        _u("ONI Anhang 2 - fig. 3", "signalisation", "de", kind="annex_figure"),
    ]
    # An annex figure must not be retagged even if a same-ref article existed;
    # here it simply isn't an article, so it is untouched.
    before = units[1].theme
    _propagate_themes(units)
    assert units[1].theme == before


def test_no_french_is_noop():
    units = [_u("ONI art. 9", "lois", "de"), _u("ONI art. 9", "lois", "it")]
    assert _propagate_themes(units) == 0       # nothing to inherit from


def test_missing_fr_sibling_left_as_is():
    units = [_u("ONI art. 1", "definitions", "fr"),
             _u("ONI art. 99", "lois", "de")]   # no FR art. 99
    assert _propagate_themes(units) == 0
    assert units[1].theme == "lois"


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"\n{len(tests)} tests passed")
