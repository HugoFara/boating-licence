"""Tests for the generated-figure layer (src/questions/diagrams.py).

The load-bearing test here is ``test_every_diagram_is_sourced``: it reads each
diagram's quoted fragment back out of the KB, so a hand-drawn figure that drifts from
the article prescribing it fails the build. A wrong diagram teaches a wrong shape,
which is worse than shipping none — so the spec is verified against the law, not
against itself.
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
        else:
            assert 1 <= len(d["column"]) <= 5, d["key"]
            for colour in d["column"]:
                assert colour in diagrams._LIGHT_COLOURS, f"{d['key']}: {colour}"
            assert isinstance(d["sidelights"], bool), d["key"]


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


def test_every_diagram_is_sourced():
    """Each diagram quotes the fragment of law that prescribes its shapes; that
    fragment must still be in the KB unit it cites. Skipped when the German KB isn't
    built (it is generated, not committed) — run `python run.py build --country DE`."""
    if not os.path.exists(KB_DE):
        print("    (skipped: data/kb.de.sqlite not built)")
        return
    kb = sqlite3.connect(KB_DE)
    for d in diagrams.DIAGRAMS:
        src = d["source"]
        rows = kb.execute("SELECT text FROM units WHERE id LIKE ?",
                          (src["unit"] + "%",)).fetchall()
        assert rows, f"{d['key']}: no KB unit {src['unit']!r}"
        assert any(src["quote"] in r[0] for r in rows), (
            f"{d['key']}: the cited article no longer contains "
            f"{src['quote']!r} — re-read {src['ref']} before touching the drawing")
    kb.close()


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
