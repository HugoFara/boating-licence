"""Tests for the cat-D (voile / sailing) scaffold.

Cat-D shares the whole cat-A core and adds one extension theme, `voile`, for
sailing technique. This checks the scaffold's invariants:
  * `voile` is a real theme and an exam-profile registry exists (A / D);
  * the cat-D profile draws from the cat-A core PLUS voile;
  * `voile` is PIN-ONLY: it is tagged only on the dedicated voile_wp Wikipedia
    sources (pin_theme), never by keyword — otherwise law articles that mention
    sailing vocab ("surface vélique", "gréement", "gîte") get stolen out of `lois`;
  * `voile` is excused from normalize's "missing theme" warning.

Run with `python tests/test_voile.py`.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import themes                                  # noqa: E402
from src.questions import schema, profile, PROFILES     # noqa: E402


def test_voile_is_a_registered_theme():
    assert "voile" in themes.THEMES
    assert themes.is_valid("voile")
    assert "voile" in themes.EXTENSION_THEMES


def test_permis_theme_sets():
    a, d = themes.PERMIS_THEMES["A"], themes.PERMIS_THEMES["D"]
    assert "voile" not in a                    # cat-A core never includes sailing
    assert d == a + ("voile",)                 # cat-D = core + voile, in order


def test_profile_registry():
    assert set(PROFILES) == {"A", "D"}
    assert profile("A").permis == "A" and "voile" not in profile("A").themes
    d = profile("d")                           # case-insensitive
    assert d.permis == "D" and "voile" in d.themes
    # cat-D mirrors the national exam structure today (only the theme set differs)
    assert (d.questions, d.total_points, d.pass_points) == (60, 180, 165)


def test_unknown_permis_raises():
    try:
        profile("Z")
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for unknown permis")


def test_voile_is_pin_only_never_keyword_tagged():
    # voile is sourced ONLY from the dedicated voile_wp sources (pin_theme); the
    # keyword tagger must NEVER return voile. Sailing vocab also appears in the LAW
    # (ONI art. 79 defines cat-D by "surface vélique > 15 m²", art. 134/137/153
    # mention gréement/gîte), so a keyword rule would mis-tag those articles.
    for text in ("Les allures : au près, au largue, vent arrière",
                 "Le virement de bord et l'empannage",
                 "Réglage du foc et de la grand-voile",
                 "Surface vélique de 12 m2"):
        assert themes.tag_theme(text=text) != "voile", text


def test_voile_source_pins_the_theme():
    from src import sources
    vw = sources.BY_ID["voile_wp"]
    assert vw.kind == "wikipedia" and vw.pin_theme == "voile"


def test_right_of_way_law_stays_lois():
    # cat-A priority rules mention "bateau à voile" but are navigation LAW, not
    # sailing technique — the voile theme must not steal them.
    text = "Le bateau à voile a la priorité sur le bateau à moteur."
    assert themes.tag_theme(text=text) == "lois"


def test_default_examconfig_is_cat_a():
    cfg = schema.ExamConfig()
    assert cfg.permis == "A"
    assert cfg.themes == themes.PERMIS_THEMES["A"]


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"\n{len(tests)} tests passed")
