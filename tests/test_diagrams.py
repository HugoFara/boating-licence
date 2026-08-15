"""Tests for the generated-figure layer (src/questions/diagrams.py).

Two load-bearing tests. ``test_every_citation_holds_in_its_own_law`` reads each
diagram's quoted fragment back out of the KB of the code that cites it, so a drawing
that drifts from the article prescribing it fails the build — one picture may serve
several countries, but its citation never transfers. And because a citation can be
perfectly real while sitting on the wrong drawing,
``test_a_citation_describes_the_figure_it_is_attached_to`` also requires the quote to
name what is actually drawn. A wrong diagram teaches a wrong shape, which is worse
than shipping none, so the spec is verified against the law and never against itself.
"""
import os
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.questions import schema                                       # noqa: E402
from src.questions.schema import Question, Choice, Provenance          # noqa: E402
from src.questions import diagrams                                     # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB_DE = os.path.join(ROOT, "data", "kb.de.sqlite")


def _conn():
    fd, path = tempfile.mkstemp(suffix=".sqlite")
    os.close(fd)
    return schema.connect(path), path


def _q(qid, stem, answer, ref, source, image=None):
    return Question(
        id=qid, theme="signalisation", kind="rule_mc", stem=stem, lang="de",
        image=image,
        choices=[Choice(answer, is_correct=True), Choice("etwas anderes")],
        provenance=Provenance(unit_id="u1", ref=ref, source=source,
                              url="https://www.elwis.de/"),
        review_status="auto_approved")


def test_render_is_deterministic_and_self_contained():
    for d in diagrams.DIAGRAMS:
        a, b = diagrams.render_one(d), diagrams.render_one(d)
        assert a == b, f"{d['key']} does not render deterministically"
        assert a.startswith("<svg ") and a.rstrip().endswith("</svg>")
        # No external reference of any kind: the player is offline-only. (The SVG
        # xmlns is a namespace name, never fetched — strip it before looking.)
        body = a.replace('xmlns="http://www.w3.org/2000/svg"', "")
        for forbidden in ("http://", "https://", "<image", "xlink:href", "<script"):
            assert forbidden not in body, f"{d['key']} pulls in {forbidden}"


def test_every_spec_is_drawable_by_its_family():
    for d in diagrams.DIAGRAMS:
        assert d["family"] in diagrams.FAMILIES, d["key"]
        if d["family"] == "day-shapes":
            assert 1 <= len(d["shapes"]) <= 3, d["key"]
            for kind, _colour in d["shapes"]:
                assert kind in diagrams._PRIMITIVES, f"{d['key']}: {kind}"
        elif d["family"] == "nav-lights":
            assert 1 <= len(d["column"]) <= 5, d["key"]
            for colour in d["column"]:
                assert colour in diagrams._LIGHT_COLOURS, f"{d['key']}: {colour}"
            assert isinstance(d["sidelights"], bool), d["key"]
        elif d["family"] == "sound-signals":
            assert d["pattern"], d["key"]
            for tok in d["pattern"]:
                assert tok in diagrams._TONE_S or tok == "gap", f"{d['key']}: {tok}"
            assert d["pattern"][0] != "gap" and d["pattern"][-1] != "gap", d["key"]
        else:
            assert len(d["boats"]) == 2, f"{d['key']}: an encounter has two vessels"
            for b in d["boats"]:
                assert b["role"] in ("give-way", "stand-on"), f"{d['key']}: {b}"
                assert b.get("boom") in (None, "port", "stbd"), f"{d['key']}: {b}"


def test_one_fixed_canvas_per_family_so_figures_are_comparable():
    """A single cylinder and a three-ball stack must render at the SAME scale — the
    learner is meant to compare shapes, never sizes. One viewBox per family is what
    guarantees that inside the player's fixed-height figure box."""
    boxes: dict[str, set] = {}
    for d in diagrams.DIAGRAMS:
        box = diagrams.render_one(d).split('viewBox="')[1].split('"')[0]
        boxes.setdefault(d["family"], set()).add(box)
    for family, seen in boxes.items():
        assert len(seen) == 1, f"{family} diagrams disagree on the canvas: {seen}"


def test_sidelights_are_drawn_as_seen_from_ahead():
    """Green to starboard, red to port (Regel 21 b) — and bows-on the vessel's
    starboard side faces the observer's LEFT. Drawing that mirrored would teach the
    exact opposite of the Rule, so it is pinned here."""
    svg = diagrams.render_lights(["white"], True, "t")
    green_x = red_x = None
    for chunk in svg.split("<circle ")[1:]:
        cx = float(chunk.split('cx="')[1].split('"')[0])
        cy = float(chunk.split('cy="')[1].split('"')[0])
        if abs(cy - diagrams._SIDE_Y) > 0.01:
            continue                                  # a column light, not a sidelight
        if diagrams._LIGHT_COLOURS["green"] in chunk:
            green_x = cx
        elif diagrams._LIGHT_COLOURS["red"] in chunk:
            red_x = cx
    assert green_x is not None and red_x is not None, "sidelights missing"
    assert green_x < red_x, "green must be left of red in a bows-on view"


def test_no_sternlight_is_ever_drawn():
    """The sternlight shines 135° from right astern (Regel 21 c), so from ahead it
    cannot be seen. Every making-way diagram must therefore show sidelights and no
    light below them — its absence is part of the lesson."""
    for d in diagrams.DIAGRAMS:
        if d["family"] != "nav-lights" or not d["sidelights"]:
            continue
        svg = diagrams.render_one(d)
        lows = [float(c.split('cy="')[1].split('"')[0])
                for c in svg.split("<circle ")[1:]]
        assert max(lows) <= diagrams._SIDE_Y, f"{d['key']} draws a light abaft"


def test_every_timeline_fits_its_canvas():
    """A blast timeline is centred on a shared canvas, so a pattern wider than the
    canvas silently runs off the edge instead of failing. Two did, because a group
    separator was charged the inter-group pause twice — once entering the gap and
    once leaving it."""
    for d in diagrams.DIAGRAMS:
        if d["family"] != "sound-signals":
            continue
        width = diagrams._pattern_width(d["pattern"], d["repeat"])
        assert width <= diagrams._SW - 24, (
            f"{d['key']} is {width:.0f}px wide on a {diagrams._SW:.0f}px canvas")


def test_a_group_separator_costs_one_pause_not_two():
    """The regression above, pinned directly: three long tones, a group break, three
    more must measure exactly two groups plus ONE inter-group pause."""
    group = 3 * 4 * diagrams._SEC + 2 * diagrams._PAUSE * diagrams._SEC
    expected = 2 * group + diagrams._GROUP_PAUSE * diagrams._SEC
    got = diagrams._pattern_width(
        ["long", "long", "long", "gap", "long", "long", "long"], False)
    assert abs(got - expected) < 0.01, f"expected {expected}, got {got}"


def test_blast_bars_are_drawn_to_scale():
    """A long blast is about four times a short one (Anlage 6 Vorbemerkung), and the
    figure has to say so — that ratio IS the discrimination in the overtaking and
    harbour signals."""
    segs, _ = diagrams._segments(["short", "long"])
    (_, short_w), (_, long_w) = segs
    assert abs(long_w / short_w - 4.0) < 0.01


def test_measure_and_draw_use_the_same_layout():
    """Centring is computed from _pattern_width and the bars from _segments; if those
    two ever disagree the figure drifts off centre. Same walk, so check they agree."""
    for d in diagrams.DIAGRAMS:
        if d["family"] != "sound-signals":
            continue
        segs, span = diagrams._segments(d["pattern"])
        assert abs(segs[-1][0] + segs[-1][1] - span) < 0.01, d["key"]
        assert diagrams._pattern_width(d["pattern"], False) == span, d["key"]


def test_layout_satisfies_the_annex_it_cites():
    """Anlage I §2 j): on a fishing vessel the lower of the two all-round lights must
    clear the sidelights by at least twice its distance from the upper one. The
    module asserts this at import; assert it here too so a geometry tweak that
    quietly breaks the annex can't ship."""
    assert diagrams._SIDE_Y - diagrams._L_BOTTOM >= 2 * diagrams._L_PITCH


def test_titles_never_leak_the_meaning():
    """The accessible name describes the SHAPES. A title that named what they mean
    would hand the answer to exactly the questions the diagram is attached to."""
    leaks = ("manövrierunfähig", "manövrierbehindert", "grundsitzer", "tiefgang",
             "fischend", "vor anker", "schleppverband", "taucher")
    for d in diagrams.DIAGRAMS:
        low = d["title"].lower()
        for word in leaks:
            assert word not in low, f"{d['key']} title leaks its meaning: {word}"


_KB_BY_REGIME = {"kvr": "kb.de.sqlite", "binschstro": "kb.de.sqlite",
                 "seeschstro": "kb.de.sqlite", "colreg": "kb.int.sqlite",
                 "oni": "kb.ch.sqlite", "rnl": "kb.ch.sqlite",
                 "code_transports": "kb.fr.sqlite"}


def test_every_citation_holds_in_its_own_law():
    """Each diagram quotes the fragment that prescribes it — once per code that
    prescribes it — and every fragment must still be in the KB unit it cites.

    This is what lets one drawing serve several countries without lying to any of
    them: the picture is shared, the citation never is. Skipped per regime when that
    KB isn't built (they are generated, not committed)."""
    checked = skipped = 0
    for d in diagrams.DIAGRAMS:
        for c in diagrams.citations(d):
            regime = diagrams.regime_of(c["unit"])
            assert regime in _KB_BY_REGIME, f"{d['key']}: unknown regime {regime!r}"
            path = os.path.join(ROOT, "data", _KB_BY_REGIME[regime])
            if not os.path.exists(path):
                skipped += 1
                continue
            kb = sqlite3.connect(path)
            rows = kb.execute("SELECT text FROM units WHERE id LIKE ?",
                              (c["unit"] + "%",)).fetchall()
            kb.close()
            assert rows, f"{d['key']}: no KB unit {c['unit']!r}"
            assert any(c["quote"] in r[0] for r in rows), (
                f"{d['key']}: {c['ref']} no longer contains {c['quote']!r} — "
                f"re-read the article before touching the drawing")
            checked += 1
    if skipped:
        print(f"    ({checked} citations checked, {skipped} skipped: KB not built)")


# What each drawn thing is called, across the four languages the codes are
# published in. A citation that names none of them is not describing this figure.
_VOCAB = {
    "ball": ("ball", "bälle", "ballon", "pallone", "balls"),
    "cone-up": ("kegel", "cone", "cône", "cono", "conical"),
    "cone-down": ("kegel", "cone", "cône", "cono", "conical"),
    "cylinder": ("zylinder", "cylinder", "cylindre", "cilindro"),
    "diamond": ("rhombus", "diamond", "losange", "rombo"),
    "hourglass": ("stundenglas", "cones", "cônes", "coni"),
    "flag-a": ("flagge", "flag", "pavillon", "panneau", "tafel", "bandiera"),
}
_LIGHT_WORDS = ("licht", "lichter", "light", "feu", "feux", "luce", "luci")
# "morse" counts: a Morse signal IS a blast grammar, and Anlage IV gives the
# distress signal as dots and dashes rather than in words.
_SOUND_WORDS = ("ton", "töne", "blast", "son", "sons", "suono", "glocke",
                "morse")
_WAY_WORDS = ("keep out of the way", "alter her course", "abaft her beam",
              "s'écarte", "s’écarte", "venir sur tribord", "tenir leur droite",
              "freilassen", "wind on the port side", "réserver aux avalants")


def test_a_citation_describes_the_figure_it_is_attached_to():
    """A citation can be perfectly real and still be on the wrong drawing — which is
    exactly what happened: ONI art. 32's diving board landed on a nav-light entry,
    and the "does this quote exist in the law" check waved it through because the
    quote was genuine. So also require the quote to name what is drawn."""
    for d in diagrams.DIAGRAMS:
        for c in diagrams.citations(d):
            q = c["quote"].lower()
            if d["family"] == "day-shapes":
                words = {w for kind, _ in d["shapes"] for w in _VOCAB[kind]}
                assert any(w in q for w in sorted(words)), (
                    f"{d['key']}: {c['ref']} names none of the shapes drawn "
                    f"({[k for k, _ in d['shapes']]}) — wrong diagram?")
            elif d["family"] == "nav-lights":
                assert any(w in q for w in _LIGHT_WORDS), (
                    f"{d['key']}: {c['ref']} does not mention a light — "
                    f"wrong diagram?")
            elif d["family"] == "give-way":
                assert any(w in q for w in _WAY_WORDS), (
                    f"{d['key']}: {c['ref']} states no duty to keep clear — "
                    f"wrong diagram?")
            else:
                assert any(w in q for w in _SOUND_WORDS), (
                    f"{d['key']}: {c['ref']} does not mention a blast — "
                    f"wrong diagram?")


def test_give_way_diagrams_are_card_only():
    """Unlike every other family, a give-way plan view SHOWS who gives way — which is
    the answer to the questions it illustrates. It is safe on a concept card, which
    opens at reveal, and never on a stem. Nothing may assign one to a question."""
    gw = {d["key"] for d in diagrams.DIAGRAMS if d["family"] == "give-way"}
    assert gw, "expected some give-way diagrams"
    for a in diagrams.ASSIGNMENTS:
        assert a["key"] not in gw, (
            f"{a['key']} would put the answer in the stem of {a['ref']}")


def test_the_two_roles_are_drawn_differently():
    """The give-way vessel alters (curved arrow, solid hull); the stand-on vessel
    holds course (straight arrow, open hull). If both rendered the same the picture
    would say nothing, so check the two actually differ."""
    give = diagrams.render_giveway(
        [{"x": 100, "y": 100, "hdg": 0, "role": "give-way"}], "t")
    stand = diagrams.render_giveway(
        [{"x": 100, "y": 100, "hdg": 0, "role": "stand-on"}], "t")
    assert "<path" in give and "<path" not in stand      # curve vs straight line
    assert diagrams._HULL_GIVE in give and diagrams._HULL_STAND in stand


def test_a_diagram_only_reaches_a_bank_its_own_law_covers():
    """Swiss inland day-shape balls are painted green, white or yellow; COLREG's are
    black. So a bank may only be offered a diagram it can cite, and the coloured
    Swiss balls must never surface on a maritime card."""
    for key in ("priority-green-ball", "trawling-white-ball", "fishing-yellow-ball"):
        assert key in diagrams.keys_for_bank("ch"), key
        assert key not in diagrams.keys_for_bank("int"), f"{key} leaked to COLREG"
        assert key not in diagrams.keys_for_bank("de"), f"{key} leaked to the KVR"
    # and the sea-only shapes must not surface on the French inland card
    assert "fishing-hourglass" not in diagrams.keys_for_bank("fr_eaux_interieures")


def test_card_strips_are_derived_not_hand_listed():
    """figures_for() must return only diagrams of the asked-for family, in spec
    order, and nothing the bank cannot cite."""
    for bank in diagrams.BANK_REGIMES:
        for family in diagrams.FAMILIES:
            keys = diagrams.figures_for(family, bank)
            assert keys == [k for k in keys], bank
            for k in keys:
                assert diagrams.BY_KEY[k]["family"] == family
                assert k in diagrams.keys_for_bank(bank)
            order = [d["key"] for d in diagrams.DIAGRAMS if d["key"] in set(keys)]
            assert keys == order, f"{bank}/{family} is out of spec order"


def test_assignments_are_well_formed():
    seen = set()
    for a in diagrams.ASSIGNMENTS:
        assert a["key"] in diagrams.BY_KEY, f"unknown diagram {a['key']}"
        assert a["why"] in diagrams._WHY, f"{a['ref']}: bad why {a['why']}"
        # prov_ref alone is NOT unique — SBF See and SBF Binnen both number from 1
        key = (a["bank"], a["catalogue"], a["ref"])
        assert key not in seen, f"duplicate assignment {key}"
        seen.add(key)


def test_attach_fills_only_the_assigned_question():
    conn, path = _conn()
    schema.write_questions(conn, [
        _q("see99", "Welches Fahrzeug führt diese Signalkörper?",
           "Ein manövrierunfähiges Fahrzeug.", "Frage 99",
           "ELWIS Fragenkatalog SBF See, Stand 01.08.2023"),
        # same reference number in the OTHER catalogue — must not be touched
        _q("binnen99", "Welche Fahrrinnenseite hat ein Bergfahrer?",
           "Die rechte Seite.", "Frage 99",
           "ELWIS Fragenkatalog SBF Binnen, Stand 01.08.2023"),
    ])
    st = diagrams.attach(conn, "de")
    by_id = {q.id: q.image for q in schema.load_questions(conn)}
    assert by_id["see99"] == diagrams.path_for("nuc-two-balls")
    assert not by_id["binnen99"], "the Binnen catalogue's Frage 99 was illustrated"
    assert st["attached"] == 1
    # idempotent: a second pass changes nothing (the figure is already there)
    st2 = diagrams.attach(conn, "de")
    assert st2["attached"] == 0 and st2["skipped"] == 1
    os.remove(path)


def test_interlock_refuses_when_the_answer_moved():
    """If the upstream catalogue renumbers, the assignment must refuse rather than
    illustrate the wrong shape."""
    conn, path = _conn()
    schema.write_questions(conn, [
        _q("see99", "Welches Fahrzeug führt diese Signalkörper?",
           "Ein fischendes Fahrzeug in Fahrt.",      # <- no longer the NUC answer
           "Frage 99", "ELWIS Fragenkatalog SBF See, Stand 01.08.2023"),
    ])
    st = diagrams.attach(conn, "de")
    assert st["attached"] == 0 and st["mismatched"] == 1
    assert not schema.load_questions(conn)[0].image  # left blank, not guessed at
    os.remove(path)


def test_interlock_refuses_a_stem_that_no_longer_points_at_a_figure():
    """A "deictic" assignment claims the stem points at a figure that was never
    shipped. If the stem gets reworded to describe the shapes in words, the picture
    might give away the answer — so the claim is re-checked, not trusted."""
    conn, path = _conn()
    schema.write_questions(conn, [
        _q("see99", "Welches Fahrzeug führt zwei schwarze Bälle senkrecht "
                    "übereinander?",                 # <- describes, does not point
           "Ein manövrierunfähiges Fahrzeug.", "Frage 99",
           "ELWIS Fragenkatalog SBF See, Stand 01.08.2023"),
    ])
    st = diagrams.attach(conn, "de")
    assert st["attached"] == 0 and st["mismatched"] == 1
    os.remove(path)


def test_attach_never_replaces_an_existing_figure():
    """An official source figure always wins over a generated one."""
    conn, path = _conn()
    schema.write_questions(conn, [
        _q("see99", "Welches Fahrzeug führt diese Signalkörper?",
           "Ein manövrierunfähiges Fahrzeug.", "Frage 99",
           "ELWIS Fragenkatalog SBF See, Stand 01.08.2023",
           image="data/assets/elwis/see/de/Bild-001.gif"),
    ])
    st = diagrams.attach(conn, "de")
    assert st["attached"] == 0 and st["skipped"] == 1
    assert schema.load_questions(conn)[0].image.endswith("Bild-001.gif")
    os.remove(path)


def test_render_all_writes_every_diagram():
    with tempfile.TemporaryDirectory() as tmp:
        st = diagrams.render_all(tmp)
        assert st["written"] == st["diagrams"] == len(diagrams.DIAGRAMS)
        out = os.path.join(tmp, diagrams.OUT_DIR)
        for d in diagrams.DIAGRAMS:
            assert os.path.exists(os.path.join(out, f"{d['key']}.svg"))
        # second run is a no-op: no churn in the tree on every build
        assert diagrams.render_all(tmp)["written"] == 0


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
