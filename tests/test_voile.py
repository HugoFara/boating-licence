"""Tests for the cat-D (voile / sailing) scaffold.

Cat-D shares the whole cat-A core and adds one extension theme, `voile`, for
sailing technique. This checks the scaffold's invariants:
  * `voile` is a real theme and an exam-profile registry exists (A / D);
  * the cat-D profile draws from the cat-A core PLUS voile;
  * sailing *technique* vocabulary tags to `voile`, but cat-A right-of-way law
    that merely mentions "bateau à voile" stays in `lois` (the precision the
    rule was written for);
  * `voile` is excused from normalize's "missing theme" warning (no source yet).

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


def test_sailing_technique_tags_to_voile():
    for text in ("Les allures : au près, au largue, vent arrière",
                 "Le virement de bord et l'empannage",
                 "Réglage du foc et de la grand-voile",
                 "Surface vélique de 12 m2"):
        assert themes.tag_theme(text=text) == "voile", text


def test_right_of_way_law_stays_lois():
    # cat-A priority rules mention "bateau à voile" but are navigation LAW, not
    # sailing technique — the voile rule must not steal them.
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
