"""Tests for the France *permis plaisance* extension (`src/fr/`, `src/countries/fr.py`).

France is seed-driven (no Fedlex pipeline): these checks pin the contract the rest
of the build relies on — the seed bank is well-formed and every entry is grounded
in a real source; the FR/EN variants stay aligned; the exam profile matches the
national format (40 q, pass 35, single-answer); and France is registered in the
country/jurisdiction registries and its themes validate.

Run with `python tests/test_fr.py`.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import themes                                      # noqa: E402
from src import countries                                   # noqa: E402
from src import scope                                        # noqa: E402
from src.questions import schema                             # noqa: E402
from src.fr import themes_fr, exam_fr, sources_fr, build_fr, derive_fr  # noqa: E402
from src.fr.seed_fr import SEED                              # noqa: E402


def test_seed_entries_well_formed():
    for i, e in enumerate(SEED):
        assert e["option"] in exam_fr.PROFILES, f"seed {i}: bad option"
        assert themes_fr.is_valid(e["theme"]), f"seed {i}: bad theme {e['theme']!r}"
        # the theme must belong to the option's exam
        assert e["theme"] in themes_fr.OPTION_THEMES[e["option"]], \
            f"seed {i}: theme {e['theme']!r} not in option {e['option']!r}"
        assert e["source"] in sources_fr.FR_SOURCES, f"seed {i}: unknown source"
        assert e["polarity"] in schema.POLARITIES
        # FR is authoritative, EN a parallel study translation
        for lg in ("fr", "en"):
            assert e[lg]["stem"].strip(), f"seed {i}/{lg}: empty stem"
        ch = e["choices"]
        assert len(ch) == 3, f"seed {i}: exam uses 3 choices"
        assert sum(1 for c in ch if c["correct"]) == 1, \
            f"seed {i}: French QCM is single-answer (exactly one correct)"
        for c in ch:
            assert c["fr"].strip() and c["en"].strip(), f"seed {i}: empty choice text"


def test_both_options_are_seeded_across_their_themes():
    by_opt = {opt: set() for opt in exam_fr.PROFILES}
    for e in SEED:
        by_opt[e["option"]].add(e["theme"])
    # every option has questions, spanning most of its theme set
    for opt, seen in by_opt.items():
        assert seen, f"option {opt} has no questions"
        assert seen <= set(themes_fr.OPTION_THEMES[opt])
        assert len(seen) >= 5, f"option {opt} covers only {len(seen)} themes"


def test_build_questions_are_valid_and_approved():
    by_option = build_fr.build_questions()
    assert set(by_option) == set(exam_fr.PROFILES)
    total = 0
    for opt, by_lang in by_option.items():
        assert set(by_lang) == {"fr", "en"}
        # FR and EN are produced one-for-one (parallel translations)
        assert len(by_lang["fr"]) == len(by_lang["en"]) > 0
        for lg, qs in by_lang.items():
            for q in qs:
                assert schema.validate(q) == [], f"{q.id}: {schema.validate(q)}"
                assert q.review_status == "approved"   # hand-authored + cited
                assert q.points == 1 and q.lang == lg
                assert q.provenance.url and q.provenance.licence
                assert len(q.correct) == 1             # single-answer
        total += len(by_lang["fr"])
    # the served bank = one FR question per seed entry + any approved law-/
    # reference-derived draft (pending drafts are excluded by the review gate).
    assert total == len(SEED) + len(derive_fr.approved_entries())


def test_exam_profiles_match_the_national_format():
    for opt in ("cotiere", "eaux_interieures"):
        cfg = exam_fr.profile(opt)
        assert (cfg.questions, cfg.total_points, cfg.pass_points) == (40, 40, 35)
        assert cfg.points_per_question == 1 and cfg.scoring == "all_or_nothing"
        assert cfg.time_limit_min == 30
        assert tuple(cfg.themes) == themes_fr.OPTION_THEMES[opt]


def test_fr_themes_registered_with_shared_validator():
    # questions carrying FR theme ids must pass the shared schema validator
    for tid in themes_fr.FR_THEMES:
        assert themes.is_valid(tid)
    # FR theme ids must not collide with the Swiss core
    assert not (set(themes_fr.FR_THEMES) & set(themes.THEMES))


def test_france_registered_in_country_registry():
    fr = countries.get("FR")
    assert fr.code == "FR" and fr.default_lang == "fr"
    assert set(fr.permits) == {"cotiere", "eaux_interieures"}
    for p in fr.permits.values():
        assert p.exam.questions == 40 and p.exam.pass_points == 35
    assert fr.sources == ()                 # seed-driven, provenance inline
    assert fr.references                    # but the law is documented


def test_scope_routes_fr_questions_to_the_right_base():
    # France de-silos into the shared scope layer (src/scope.py): every question
    # classifies, and the maritime/inland split follows the regime tree — RIPAM
    # (côtière) → colregs, the inland code (eaux intérieures) → cevni. No leak across
    # tracks, and the permit/equipment statute stays out of any portable base.
    by_option = build_fr.build_questions()
    for opt, by_lang in by_option.items():
        scopes = {scope.classify(q) for q in by_lang["fr"]}
        assert scopes <= scope.SCOPES
        if opt == "cotiere":
            assert "colregs" in scopes and "cevni" not in scopes
        else:
            assert "cevni" in scopes and "colregs" not in scopes
        # FR and EN variants of the same item must land in the same base.
        for fr_q, en_q in zip(by_lang["fr"], by_lang["en"]):
            assert scope.classify(fr_q) == scope.classify(en_q)
    # Spot-check the theme routing that the whole split rests on.
    pick = {(e["option"], e["theme"]): e for e in SEED}
    cases = {
        ("cotiere", "balisage"): "colregs",
        ("cotiere", "regles_route"): "colregs",
        ("cotiere", "reglementation"): "national",
        ("eaux_interieures", "voies_navigables"): "cevni",
        ("eaux_interieures", "regles_route"): "cevni",
        ("eaux_interieures", "reglementation"): "national",
    }
    qs = {(e["option"], e["theme"]): build_fr._question(e, "fr", i)
          for i, e in enumerate(SEED)}
    for key, want in cases.items():
        if key in pick:
            assert scope.classify(qs[key]) == want, f"{key} → {scope.classify(qs[key])}"


def test_core_bundle_holds_only_portable_questions():
    # The harmonised core a learner can drill is universal ∪ cevni ∪ colregs — the
    # national/local overlay (permis, Division-240 kit) must never enter it.
    by_option = build_fr.build_questions()
    for opt, by_lang in by_option.items():
        core = scope.core_bank(by_lang["fr"])
        assert core, f"{opt}: empty core"
        assert all(scope.classify(q) in scope.BASES for q in core)
        # the core is a strict subset of the national bank (overlays dropped)
        assert len(core) < len(by_lang["fr"])
        bases = scope.bases_present(by_lang["fr"])
        assert "universal" in bases
        assert ("colregs" in bases) == (opt == "cotiere")
        assert ("cevni" in bases) == (opt == "eaux_interieures")


def test_stable_ids_are_unique():
    by_option = build_fr.build_questions()
    ids = [q.id for by_lang in by_option.values()
           for qs in by_lang.values() for q in qs]
    assert len(ids) == len(set(ids)), "question ids must be unique"


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"\n{len(tests)} tests passed")
