"""Tests for per-canton exam variance (`src/cantons.py` + `profile()` overlay).

The theory exam is intercantonally standardised (VKS): 60 q / 180 pts / pass 165
and the content are national; only the time limit varies by canton. These checks
pin that contract: the registry is well-formed, only Geneva and Vaud are flagged
as Léman cantons (Valais is upstream, the south shore is French), Bern carries
the documented 45-minute variant, and `profile()` overlays the canton's timer
onto a permit profile WITHOUT touching the national count/points/pass mark.

Run with `python tests/test_cantons.py`.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import cantons                                 # noqa: E402
from src.questions import schema                        # noqa: E402


def test_registry_well_formed():
    assert set(cantons.CANTONS) >= {"GE", "VD", "BE"}
    for code, c in cantons.CANTONS.items():
        assert c.code == code
        assert c.name and isinstance(c.time_limit_min, int) and c.time_limit_min > 0


def test_leman_cantons_are_only_ge_and_vd():
    leman = {code for code, c in cantons.CANTONS.items() if c.leman}
    assert leman == {"GE", "VD"}            # Valais is upstream; south shore is FR


def test_bern_is_the_45_minute_variant():
    assert cantons.CANTONS["BE"].time_limit_min == 45
    assert cantons.CANTONS["GE"].time_limit_min == cantons.VKS_TIME_LIMIT_MIN == 50


def test_get_is_case_insensitive_and_defaults():
    assert cantons.get("ge").code == "GE"
    assert cantons.get(None).code == cantons.DEFAULT_CANTON
    assert cantons.get("").code == cantons.DEFAULT_CANTON
    try:
        cantons.get("ZZ")
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for unknown canton")


def test_profile_overlays_only_the_timer():
    ge = schema.profile("A", "GE")
    be = schema.profile("A", "BE")
    # the national standard is untouched by the canton
    for cfg in (ge, be):
        assert (cfg.questions, cfg.total_points, cfg.pass_points) == (60, 180, 165)
    # only the time limit (and the display fields) differ
    assert ge.time_limit_min == 50 and be.time_limit_min == 45
    assert ge.canton_code == "GE" and be.canton_code == "BE"
    assert "GE" in ge.canton_default and "BE" in be.canton_default


def test_canton_composes_with_permis():
    d_be = schema.profile("D", "BE")
    assert d_be.permis == "D" and "voile" in d_be.themes   # permit theme set kept
    assert d_be.time_limit_min == 45                       # canton overlay applied


def test_manifest_shape_for_player():
    man = cantons.as_manifest()
    assert [c["code"] for c in man][:2] == ["GE", "VD"]     # Léman cantons first
    assert all({"code", "name", "time_limit_min", "leman"} <= set(c) for c in man)


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"\n{len(tests)} tests passed")
