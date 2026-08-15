"""Generated figures — the day-shapes pilot (roadmap: illustration system).

Why this module exists
----------------------
560 of the 737 principle-tagged questions ship with **no picture**, and 27 German
questions are literally unanswerable as shipped: their stem says *"Welches Fahrzeug
führt diese Signalkörper?"* — *these* shapes — and no figure follows. The images we
*do* have are scraped rasters from two sources with incompatible reuse terms (ONI/RNL
via Fedlex, public domain; ELWIS GIFs, §5(2) UrhG verbatim-only), so a diagram
obtained for one country's bank cannot legally be reused in another's. That is the
opposite of what `docs/scope.md` promises for the harmonised core.

The way out is that day shapes are **geometry, not artwork**: the law describes them
as balls, cones, cylinders, diamonds and hourglasses stacked in a vertical line. So we
do not *obtain* the picture, we **derive** it — from the article that prescribes it,
with the same discipline as a question:

  * every diagram carries a ``source`` naming the unit, the article and the exact
    ``quote`` that prescribes the shapes. ``tests/test_diagrams.py`` reads that quote
    back out of the KB, so a diagram that drifts from the law fails the build rather
    than teaching a learner a wrong shape (a wrong diagram is worse than none);
  * nothing is drawn from memory. If the law does not say it, it is not in the spec;
  * the output is our own artwork under the project licence, so one diagram serves
    every bank and every language — which no scraped source image can do.

What it does *not* do
---------------------
It never attaches a diagram where the shape **is the answer**. "What signal does a
vessel unable to manoeuvre show?" must not be illustrated in its own stem. Diagrams
are attached only where the figure is the *subject* of the question — the
"which vessel shows these shapes?" pattern — which is exactly the set that is broken
today. The answer-side questions are served by the concept card instead.

Output: ``data/assets/diagrams/<key>.svg``. The existing image plumbing takes it from
there — ``run.py`` relocates any ``data/assets/...`` path into each player bundle, and
``web/app.js`` renders ``q.image`` as a plain ``<img>``. No player change is needed.
"""

from __future__ import annotations

import os
import sqlite3

FAMILY = "day-shapes"
GENERATOR = "gen:diagram.day_shapes.v1"

# Where the rendered figures land, relative to the repo root. Under data/assets/ so
# the per-country and core web bundlers relocate them like any other figure.
OUT_DIR = os.path.join("data", "assets", "diagrams")

# ── Geometry ──────────────────────────────────────────────────────────────────
# One fixed canvas for the whole family. The stack is centred in it, so a single
# cylinder and a three-ball stack render at the SAME scale in the player's
# fixed-height figure box — the learner compares shapes, never sizes.
_W, _H = 120.0, 200.0
_CX = _W / 2
_SLOT = 34.0          # height of one shape's box
_GAP = 18.0           # clear air between two stacked shapes (the law's "1 m apart")
_INK = "#111"
_STROKE = 2.0

# The primitives the law actually names. Keys are the words the articles use.
_PRIMITIVES = ("ball", "cone-up", "cone-down", "cylinder", "diamond", "hourglass",
               "flag-a")


def _shape_svg(kind: str, cy: float, colour: str) -> str:
    """One primitive, vertically centred on ``cy`` and horizontally on the mast.

    Every primitive keeps the same visual weight (a ~34 px box) so the stack reads as
    a sequence of shapes rather than a sequence of sizes."""
    fill = colour
    r = _SLOT / 2
    if kind == "ball":
        return (f'<circle cx="{_CX}" cy="{cy}" r="{r}" '
                f'fill="{fill}" stroke="{_INK}" stroke-width="{_STROKE}"/>')
    if kind in ("cone-up", "cone-down"):
        hw = r * 0.95
        if kind == "cone-up":
            pts = f"{_CX},{cy - r} {_CX - hw},{cy + r} {_CX + hw},{cy + r}"
        else:
            pts = f"{_CX},{cy + r} {_CX - hw},{cy - r} {_CX + hw},{cy - r}"
        return (f'<polygon points="{pts}" fill="{fill}" stroke="{_INK}" '
                f'stroke-width="{_STROKE}" stroke-linejoin="round"/>')
    if kind == "cylinder":
        hw, ry = r * 0.72, 5.0
        top, bot = cy - r + ry, cy + r - ry
        # body + a visible top ellipse, so it can't be mistaken for a plain rectangle
        return (f'<path d="M{_CX - hw},{top} L{_CX - hw},{bot} '
                f'A{hw},{ry} 0 0 0 {_CX + hw},{bot} L{_CX + hw},{top} Z" '
                f'fill="{fill}" stroke="{_INK}" stroke-width="{_STROKE}"/>'
                f'<ellipse cx="{_CX}" cy="{top}" rx="{hw}" ry="{ry}" '
                f'fill="{fill}" stroke="{_INK}" stroke-width="{_STROKE}"/>')
    if kind == "diamond":
        hw = r * 0.80
        pts = (f"{_CX},{cy - r} {_CX + hw},{cy} {_CX},{cy + r} {_CX - hw},{cy}")
        return (f'<polygon points="{pts}" fill="{fill}" stroke="{_INK}" '
                f'stroke-width="{_STROKE}" stroke-linejoin="round"/>')
    if kind == "hourglass":
        # "ein Stundenglas" (Regel 26) — two cones apex to apex.
        hw = r * 0.95
        pts = (f"{_CX - hw},{cy - r} {_CX + hw},{cy - r} {_CX - hw},{cy + r} "
               f"{_CX + hw},{cy + r}")
        return (f'<polygon points="{pts}" fill="{fill}" stroke="{_INK}" '
                f'stroke-width="{_STROKE}" stroke-linejoin="round"/>')
    if kind == "flag-a":
        # International Code flag "A" as a board (Regel 27 e ii): hoist half white,
        # fly half blue, swallow-tailed.
        hw, hh = r * 1.15, r * 0.78
        x0, x1 = _CX - hw, _CX + hw
        y0, y1 = cy - hh, cy + hh
        mid = _CX
        notch = x1 - hw * 0.45
        return (f'<path d="M{x0},{y0} L{mid},{y0} L{mid},{y1} L{x0},{y1} Z" '
                f'fill="#fff" stroke="{_INK}" stroke-width="{_STROKE}"/>'
                f'<path d="M{mid},{y0} L{x1},{y0} L{notch},{cy} L{x1},{y1} '
                f'L{mid},{y1} Z" fill="#1d4ed8" stroke="{_INK}" '
                f'stroke-width="{_STROKE}" stroke-linejoin="round"/>')
    raise ValueError(f"unknown primitive {kind!r}; expected one of {_PRIMITIVES}")


def render(shapes: list[tuple[str, str]], title: str, source_ref: str = "") -> str:
    """Render a vertical stack of shapes, top of the list = top of the mast.

    ``title`` describes the *shapes*, never what they mean — the diagram is the
    question, so an accessible name that gave away the answer would defeat it. The
    citation goes in an XML comment rather than a ``<desc>`` for the same reason: it
    attributes the drawing without a screen reader announcing the answer."""
    n = len(shapes)
    if not 1 <= n <= 3:
        raise ValueError(f"a day-shape stack holds 1–3 shapes, got {n}")
    span = n * _SLOT + (n - 1) * _GAP
    top = (_H - span) / 2 - 6          # a touch high; the mast foot balances it
    credit = (f"\n<!-- Generated figure, derived from {source_ref}. Original artwork; "
              f"project licence (CC BY-SA 4.0), not a reproduction of any source "
              f"figure. {GENERATOR} -->" if source_ref else "")
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {_W:g} {_H:g}" '
             f'width="{_W:g}" height="{_H:g}" role="img" '
             f'aria-label="{_esc(title)}">{credit}',
             f'<title>{_esc(title)}</title>',
             # the mast: it is what makes "senkrecht übereinander" legible
             f'<rect x="{_CX - 1.5:g}" y="{top - 12:g}" width="3" '
             f'height="{span + 40:g}" fill="#6b7280"/>',
             f'<rect x="{_CX - 17:g}" y="{top + span + 26:g}" width="34" height="4" '
             f'rx="2" fill="#6b7280"/>']
    for i, (kind, colour) in enumerate(shapes):
        cy = top + i * (_SLOT + _GAP) + _SLOT / 2
        parts.append(_shape_svg(kind, cy, colour))
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def _esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


# ── The spec ──────────────────────────────────────────────────────────────────
# One entry per distinct configuration, NOT per question — the whole point is that a
# handful of diagrams covers hundreds of questions across banks and languages.
#
# ``source.quote`` is the load-bearing field: it is the fragment of the cited article
# that prescribes these shapes, and tests/test_diagrams.py asserts it still occurs in
# ``source.unit``'s text in the KB. That is what keeps a hand-drawn figure honest.
DIAGRAMS: list[dict] = [
    {
        "key": "nuc-two-balls",
        "shapes": [("ball", _INK), ("ball", _INK)],
        "title": "Zwei schwarze Bälle senkrecht übereinander",
        "source": {
            "unit": "kvr-de-seestro_1972_regel_27",
            "ref": "SeeStrO 1972 Regel 27 Buchstabe a Ziffer ii",
            "quote": "zwei Bälle oder ähnliche Signalkörper senkrecht übereinander",
        },
    },
    {
        "key": "ram-ball-diamond-ball",
        "shapes": [("ball", _INK), ("diamond", _INK), ("ball", _INK)],
        "title": "Ball, Rhombus, Ball senkrecht übereinander",
        "source": {
            "unit": "kvr-de-seestro_1972_regel_27",
            "ref": "SeeStrO 1972 Regel 27 Buchstabe b Ziffer ii",
            "quote": "Der obere und der untere Signalkörper müssen Bälle, der "
                     "mittlere muß ein Rhombus sein",
        },
    },
    {
        "key": "aground-three-balls",
        "shapes": [("ball", _INK), ("ball", _INK), ("ball", _INK)],
        "title": "Drei schwarze Bälle senkrecht übereinander",
        "source": {
            "unit": "kvr-de-seestro_1972_regel_30",
            "ref": "SeeStrO 1972 Regel 30 Buchstabe d Ziffer ii",
            "quote": "drei Bälle senkrecht übereinander",
        },
    },
    {
        "key": "draft-cylinder",
        "shapes": [("cylinder", _INK)],
        "title": "Ein schwarzer Zylinder",
        "source": {
            "unit": "kvr-de-seestro_1972_regel_28",
            "ref": "SeeStrO 1972 Regel 28",
            "quote": "oder einen Zylinder dort führen",
        },
    },
    {
        "key": "fishing-hourglass",
        "shapes": [("hourglass", _INK)],
        "title": "Ein Stundenglas (zwei Kegel, Spitze an Spitze)",
        "source": {
            "unit": "kvr-de-seestro_1972_regel_26",
            "ref": "SeeStrO 1972 Regel 26 Buchstabe c Ziffer i",
            "quote": "das obere rot und das untere weiß, oder ein Stundenglas",
        },
    },
    {
        "key": "tow-diamond",
        "shapes": [("diamond", _INK)],
        "title": "Ein schwarzer Rhombus",
        "source": {
            "unit": "kvr-de-seestro_1972_regel_24",
            "ref": "SeeStrO 1972 Regel 24 Buchstabe a Ziffer v",
            "quote": "einen rhombusförmigen Signalkörper",
        },
    },
    {
        "key": "sail-under-power-cone-down",
        "shapes": [("cone-down", _INK)],
        "title": "Ein schwarzer Kegel, Spitze nach unten",
        "source": {
            "unit": "kvr-de-seestro_1972_regel_25",
            "ref": "SeeStrO 1972 Regel 25 Buchstabe e",
            "quote": "im Vorschiff einen Kegel - Spitze unten - dort führen",
        },
    },
    {
        "key": "fishing-gear-cone-up",
        "shapes": [("cone-up", _INK)],
        "title": "Ein schwarzer Kegel, Spitze nach oben",
        "source": {
            "unit": "kvr-de-seestro_1972_regel_26",
            "ref": "SeeStrO 1972 Regel 26 Buchstabe c Ziffer ii",
            "quote": "einen Kegel - Spitze oben - in Richtung des Fanggeräts",
        },
    },
    {
        "key": "anchor-ball",
        "shapes": [("ball", _INK)],
        "title": "Ein schwarzer Ball",
        "source": {
            "unit": "kvr-de-seestro_1972_regel_30",
            "ref": "SeeStrO 1972 Regel 30 Buchstabe a Ziffer i",
            "quote": "ein weißes Rundumlicht oder einen Ball",
        },
    },
    {
        "key": "diving-flag-a",
        "shapes": [("flag-a", "#fff")],
        "title": "Die Flagge « A » des Internationalen Signalbuchs als Tafel",
        "source": {
            "unit": "kvr-de-seestro_1972_regel_27",
            "ref": "SeeStrO 1972 Regel 27 Buchstabe e Ziffer ii",
            "quote": 'die Flagge "A" des Internationalen Signalbuchs als Tafel',
        },
    },
]

BY_KEY: dict[str, dict] = {d["key"]: d for d in DIAGRAMS}


def path_for(key: str) -> str:
    """Repo-relative path of a rendered diagram (the value stored in Question.image)."""
    return f"{OUT_DIR}/{key}.svg".replace(os.sep, "/")


def render_all(root: str = ".") -> dict:
    """Render every diagram to ``data/assets/diagrams/``. Deterministic: same spec in,
    byte-identical files out, so re-running never churns the tree."""
    out = os.path.join(root, OUT_DIR)
    os.makedirs(out, exist_ok=True)
    written = 0
    for d in DIAGRAMS:
        svg = render(d["shapes"], d["title"], d["source"]["ref"])
        dst = os.path.join(out, f"{d['key']}.svg")
        old = None
        if os.path.exists(dst):
            with open(dst, encoding="utf-8") as fh:
                old = fh.read()
        if old != svg:
            with open(dst, "w", encoding="utf-8") as fh:
                fh.write(svg)
            written += 1
    return {"diagrams": len(DIAGRAMS), "written": written}


# ── The join ──────────────────────────────────────────────────────────────────
# Deliberately explicit, never fuzzy. A hand-authored assignment is keyed by the
# catalogue's own question reference plus its catalogue — ``prov_ref`` alone is NOT
# unique (SBF See and SBF Binnen both number their questions from 1), and the whole
# key is stable across rebuilds, unlike the hashed question id.
#
# ``why`` records the ground on which illustrating this question is safe. There are
# exactly two, and a diagram may never be attached on any other:
#
#   ``deictic``       the stem points at a figure that was never shipped — "Welches
#                     Fahrzeug führt *diese* Signalkörper?". These questions are
#                     unanswerable as they stand; the figure IS the question.
#   ``named-in-stem`` the stem already names the shape in words ("… einen schwarzen
#                     Rhombus führt"), so the picture restates the stem and cannot
#                     give away an answer the stem was withholding.
#
# Never attach where the shape is the ANSWER ("what signal does a vessel unable to
# manoeuvre show?") — that turns a question into a giveaway. Those are served by the
# concept card at reveal time instead.
#
# ``expect`` is a safety interlock: the substring must still occur in the question's
# correct answer. If the upstream catalogue is renumbered or reworded, the assignment
# refuses to fire instead of silently illustrating the wrong shape.
_WHY = ("deictic", "named-in-stem")

# Demonstratives a deictic stem uses to point at its missing figure. Checked at
# attach time, so a reworded catalogue can't quietly turn a deictic claim false.
_DEICTIC = ("diese ", "dieses ", "diesen ", "this ", "these ", "ce ", "ces ",
            "cette ", "questo ", "questi ", "queste ")

ASSIGNMENTS: list[dict] = [
    {"bank": "de", "catalogue": "SBF See", "ref": "Frage 96", "expect": "200 m",
     "key": "tow-diamond", "why": "named-in-stem"},
    {"bank": "de", "catalogue": "SBF See", "ref": "Frage 99",
     "expect": "manövrierunfähiges", "key": "nuc-two-balls", "why": "deictic"},
    {"bank": "de", "catalogue": "SBF See", "ref": "Frage 104",
     "expect": "manövrierbehindertes", "key": "ram-ball-diamond-ball",
     "why": "deictic"},
    {"bank": "de", "catalogue": "SBF See", "ref": "Frage 106",
     "expect": "Grundsitzer", "key": "aground-three-balls", "why": "deictic"},
    {"bank": "de", "catalogue": "SBF See", "ref": "Frage 109",
     "expect": "tiefgangbehindertes", "key": "draft-cylinder", "why": "deictic"},
    {"bank": "de", "catalogue": "SBF See", "ref": "Frage 112",
     "expect": "fischendes", "key": "fishing-hourglass", "why": "deictic"},
]


def attach(conn: sqlite3.Connection, bank_id: str, overwrite: bool = False) -> dict:
    """Fill ``Question.image`` for this bank's assigned questions.

    Never touches a question that already carries a figure (unless ``overwrite``), and
    never touches question text — which matters for the German bank, where the ELWIS
    catalogue is reusable only *unverändert*. A diagram is added *alongside* the
    verbatim question, exactly like the concept card and the choice rationales."""
    # ``missing``    the cited question isn't in this bank at all (a partially built
    #                bank, or a reference that vanished upstream);
    # ``mismatched`` it IS there but an interlock tripped — the answer or the stem is
    #                no longer the one the diagram was drawn for. That one is loud.
    stats = {"attached": 0, "skipped": 0, "mismatched": 0, "missing": 0}
    for a in ASSIGNMENTS:
        if a["bank"] != bank_id:
            continue
        if a["why"] not in _WHY:
            raise ValueError(f"assignment {a['ref']}: 'why' must be one of {_WHY}")
        rows = conn.execute(
            "SELECT id, stem, COALESCE(image,'') FROM questions "
            "WHERE prov_ref = ? AND prov_source LIKE ?",
            (a["ref"], f"%{a['catalogue']}%")).fetchall()
        if not rows:
            stats["missing"] += 1
            continue
        for qid, stem, image in rows:
            if image and not overwrite:
                stats["skipped"] += 1
                continue
            answers = [r[0] for r in conn.execute(
                "SELECT text FROM choices WHERE question_id = ? AND is_correct = 1",
                (qid,))]
            # the interlocks: the answer must still be the one the diagram was drawn
            # for, and a "deictic" claim must still be true of the stem.
            if not any(a["expect"].lower() in t.lower() for t in answers):
                stats["mismatched"] += 1
                continue
            if a["why"] == "deictic" and not any(d in stem.lower() for d in _DEICTIC):
                stats["mismatched"] += 1
                continue
            conn.execute("UPDATE questions SET image = ? WHERE id = ?",
                         (path_for(a["key"]), qid))
            stats["attached"] += 1
    conn.commit()
    return stats
