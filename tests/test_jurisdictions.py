"""Tests for the descriptive jurisdiction layer (`src/jurisdictions.py`).

Jurisdictions sit over the operational `src/countries` registry and add the two
things a `Country` cannot carry: the CEVNI relation (the portability fact) and
regimes that are not countries (CEVNI itself; Lake Constance / Bodensee, which is
*outside* CEVNI). These checks pin that the country entries are derived (not
duplicated), the non-country regimes exist with the right relation, and the
CEVNI-excluded guard recognises Bodensee wording.

Run with `python tests/test_jurisdictions.py`.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import jurisdictions, countries                # noqa: E402


def test_country_jurisdictions_are_derived_from_the_registry():
    for code in countries.codes():
        j = jurisdictions.get(code)
        assert j.kind == "country"
        assert j.derives_from == code
        assert j.name == countries.get(code).name        # one source of truth, no drift
        assert j.cevni_relation == "implements"           # every modelled country enacts CEVNI


def test_cevni_is_modelled_as_the_supra_national_core():
    c = jurisdictions.get("CEVNI")
    assert c.kind == "supra_national" and c.cevni_relation == "is_cevni"


def test_bodensee_is_a_non_cevni_shared_water_regime():
    b = jurisdictions.get("bodensee")                     # case-insensitive
    assert b.kind == "shared_water"
    assert b.cevni_relation == "excluded"                 # the whole point of the layer
    assert {"CH", "DE", "AT"} <= set(b.members)


def test_excluded_regime_guard_recognises_bodensee():
    assert jurisdictions.excluded_regime("Signal selon la BSO sur le Bodensee") == "BODENSEE"
    assert jurisdictions.excluded_regime("Lac de Constance, règle locale") == "BODENSEE"
    assert jurisdictions.excluded_regime("ONI art. 2 — définitions") is None
    assert jurisdictions.excluded_regime("") is None


def test_get_defaults_and_rejects_unknown():
    assert jurisdictions.get(None).code == jurisdictions.DEFAULT
    assert jurisdictions.get("").code == jurisdictions.DEFAULT
    try:
        jurisdictions.get("ZZ")
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for unknown jurisdiction")


def test_codes_order_countries_first_default_first():
    cs = jurisdictions.codes()
    assert cs[0] == jurisdictions.DEFAULT                 # default country leads
    # every country precedes every non-country regime
    kinds = [jurisdictions.get(c).kind for c in cs]
    last_country = max(i for i, k in enumerate(kinds) if k == "country")
    first_other = min(i for i, k in enumerate(kinds) if k != "country")
    assert last_country < first_other
    assert set(cs) >= {"CH", "CEVNI", "BODENSEE"}


def test_relations_are_in_the_controlled_vocabulary():
    for code in jurisdictions.codes():
        assert jurisdictions.relation(code) in jurisdictions.RELATIONS
        assert jurisdictions.get(code).kind in jurisdictions.KINDS


def test_manifest_shape_for_player():
    man = jurisdictions.as_manifest()
    assert [m["code"] for m in man][0] == jurisdictions.DEFAULT
    assert all({"code", "name", "kind", "cevni_relation", "members"} <= set(m) for m in man)


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"\n{len(tests)} tests passed")
