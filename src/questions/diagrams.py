"""Generated figures — day shapes, navigation lights, sound signals.

Why this module exists
----------------------
560 of the 737 principle-tagged questions ship with **no picture**, and 27 German
questions are literally unanswerable as shipped: their stem says *"Welches Fahrzeug
führt diese Signalkörper?"* — *these* shapes — and no figure follows. The images we
*do* have are scraped rasters from two sources with incompatible reuse terms (ONI/RNL
via Fedlex, public domain; ELWIS GIFs, §5(2) UrhG verbatim-only), so a diagram
obtained for one country's bank cannot legally be reused in another's. That is the
opposite of what `docs/scope.md` promises for the harmonised core.

The way out is that every family here is **geometry, not artwork**. The law describes
day shapes as balls, cones, cylinders, diamonds and hourglasses stacked in a vertical
line; it describes lights by colour, arc and vertical order (Regeln 21–30 for what a
vessel shows, Anlage I §2 for where each light sits); and it describes sound signals
as blasts of stated duration separated by a stated pause. So we do not *obtain* the
picture, we **derive** it — from the article that prescribes it, with the same
discipline as a question:

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

It also declines to draw an arrangement the source does not fix. Where a Rule stacks
one group of lights on another without saying which sits where, the question stays
unillustrated rather than have us invent the geometry — see ``_UNPRESCRIBED``.

Output: ``data/assets/diagrams/<key>.svg``. The existing image plumbing takes it from
there — ``run.py`` relocates any ``data/assets/...`` path into each player bundle, and
``web/app.js`` renders ``q.image`` as a plain ``<img>``. No player change is needed.
"""

from __future__ import annotations

import os
import sqlite3

GENERATOR = "gen:diagram.v1"
FAMILIES = ("day-shapes", "nav-lights", "sound-signals", "give-way")

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


# ── Nav-lights geometry ───────────────────────────────────────────────────────
# The view is FROM AHEAD, which is the only aspect that shows both sidelights and
# is what the "which vessel carries these lights?" questions depict. Two
# consequences, both load-bearing:
#
#   * green appears on the viewer's LEFT and red on the viewer's RIGHT — the
#     vessel's starboard side faces the observer's left when bows-on. Get this
#     backwards and the diagram teaches the opposite of Regel 21 b).
#   * the sternlight is NOT drawn. It shines over 135° from right astern
#     (Regel 21 c), so from ahead it is invisible — drawing it would be a lie, and
#     its absence is itself the lesson.
#
# The vertical layout is not invented either. Anlage I fixes it:
#   §2 f) i)  masthead lights higher than all other lights → they head the column
#   §2 g)     sidelights at most ¾ of the forward masthead height → they sit low
#   §2 i) iii) three lights in a vertical line are equally spaced → constant pitch
#   §2 k)     of two anchor lights the forward one is the higher → it leads
# So a diagram states the order the law states, and nothing more. Where an article
# leaves the order between two GROUPS of lights open (a vessel aground shows anchor
# lights "plus" two red all-round, with no rule on which sits where), no diagram is
# drawn at all — see the note on ``_UNPRESCRIBED`` below.
_LW, _LH = 160.0, 220.0
_LCX = _LW / 2
_L_PITCH = 22.0        # centre-to-centre of two lights in a vertical line
_L_BOTTOM = 116.0      # the lowest column light; the column grows upward from here
_L_R = 7.5             # light radius
_SIDE_DX = 44.0        # sidelights at or near the vessel's sides (Anlage I §3 b)
_SIDE_Y = 165.0
_DECK_Y = 172.0
_NIGHT = "#0d1626"

# The column/sidelight separation is not a styling choice — three clauses of
# Anlage I §2 bound it, and the drawing has to satisfy all three at once:
#   g)  sidelights no higher than ¾ of the forward masthead's height
#   i)  lights in a vertical line evenly spaced, the lowest well clear of the hull
#   j)  on a fishing vessel the LOWER of the two all-round lights must clear the
#       sidelights by at least twice its distance from the upper one
# (j) is the binding one: it forces _L_BOTTOM − _SIDE_Y ≥ 2 × _L_PITCH.
assert _SIDE_Y - _L_BOTTOM >= 2 * _L_PITCH, "violates Anlage I §2 j)"

# The colours the Rules name. A light is a lens colour, not a shade choice.
_LIGHT_COLOURS = {
    "white": "#fdfdf2",
    "red": "#ef4444",
    "green": "#22c55e",
    "yellow": "#facc15",
}


def _light(cx: float, cy: float, colour: str) -> str:
    """One light: a solid lens inside a soft halo, so colour survives at thumbnail
    size in the player's figure box."""
    if colour not in _LIGHT_COLOURS:
        raise ValueError(f"unknown light colour {colour!r}; "
                         f"the Rules name {tuple(_LIGHT_COLOURS)}")
    hue = _LIGHT_COLOURS[colour]
    return (f'<circle cx="{cx:g}" cy="{cy:g}" r="{_L_R * 2.1:g}" fill="{hue}" '
            f'opacity="0.22"/>'
            f'<circle cx="{cx:g}" cy="{cy:g}" r="{_L_R * 1.45:g}" fill="{hue}" '
            f'opacity="0.35"/>'
            f'<circle cx="{cx:g}" cy="{cy:g}" r="{_L_R:g}" fill="{hue}" '
            f'stroke="#00000055" stroke-width="0.75"/>')


def render_lights(column: list[str], sidelights: bool, title: str,
                  source_ref: str = "") -> str:
    """A vessel seen from ahead at night.

    ``column`` lists the centreline lights **top to bottom**, in the order the Rules
    prescribe them. ``sidelights`` is the making-way tell: several Rules prescribe
    the identity lights always but the sidelights only "bei Fahrt durchs Wasser", so
    their presence or absence is what separates a pair of otherwise identical
    questions."""
    if not 1 <= len(column) <= 5:
        raise ValueError(f"a light column holds 1–5 lights, got {len(column)}")
    credit = (f"\n<!-- Generated figure, derived from {source_ref}; layout per "
              f"SeeStrO 1972 Anlage I §2. Original artwork; project licence "
              f"(CC BY-SA 4.0), not a reproduction of any source figure. "
              f"{GENERATOR} -->" if source_ref else "")
    top = _L_BOTTOM - (len(column) - 1) * _L_PITCH
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {_LW:g} {_LH:g}" '
        f'width="{_LW:g}" height="{_LH:g}" role="img" '
        f'aria-label="{_esc(title)}">{credit}',
        f'<title>{_esc(title)}</title>',
        f'<rect width="{_LW:g}" height="{_LH:g}" fill="{_NIGHT}"/>',
        # waterline, so the picture reads as a vessel and not a free-floating mast
        f'<rect x="0" y="196" width="{_LW:g}" height="{_LH - 196:g}" '
        f'fill="#08101c"/>',
        # bows-on hull: a stem line down the middle is what makes the aspect legible
        f'<path d="M{_LCX - 60:g},196 L{_LCX - 50:g},{_DECK_Y:g} '
        f'L{_LCX + 50:g},{_DECK_Y:g} L{_LCX + 60:g},196 Z" fill="#1c2b45" '
        f'stroke="#44598a" stroke-width="1.5"/>',
        f'<line x1="{_LCX:g}" y1="{_DECK_Y:g}" x2="{_LCX:g}" y2="196" '
        f'stroke="#44598a" stroke-width="1.5"/>',
        # the mast, carrying the centreline column
        f'<rect x="{_LCX - 1:g}" y="{top - 10:g}" width="2" '
        f'height="{_DECK_Y + 6 - (top - 10):g}" fill="#44598a"/>',
    ]
    for i, colour in enumerate(column):
        parts.append(_light(_LCX, top + i * _L_PITCH, colour))
    if sidelights:
        # Regel 21 b): green to starboard, red to port. Seen from AHEAD, the vessel's
        # starboard side is on the observer's left — hence green left, red right.
        parts.append(_light(_LCX - _SIDE_DX, _SIDE_Y, "green"))
        parts.append(_light(_LCX + _SIDE_DX, _SIDE_Y, "red"))
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


# ── The spec ──────────────────────────────────────────────────────────────────
# One entry per distinct configuration, NOT per question — the whole point is that a
# handful of diagrams covers hundreds of questions across banks and languages.
#
# ``source.quote`` is the load-bearing field: it is the fragment of the cited article
# that prescribes these shapes, and tests/test_diagrams.py asserts it still occurs in
# ``source.unit``'s text in the KB. That is what keeps a hand-drawn figure honest.
DAY_SHAPES: list[dict] = [
    {
        "key": "nuc-two-balls",
        "shapes": [("ball", _INK), ("ball", _INK)],
        "title": "Zwei schwarze Bälle senkrecht übereinander",
        "source": {
            "unit": "kvr-de-seestro_1972_regel_27",
            "ref": "SeeStrO 1972 Regel 27 Buchstabe a Ziffer ii",
            "quote": "zwei Bälle oder ähnliche Signalkörper senkrecht übereinander",
        },
        "cites": [
            {"unit": "rnl-rnl_art_38",
             "ref": "RNL art. 38 al. 1 let. b (RS 747.221.1)",
             "quote": "deux ballons noirs superposés à 1 m environ de distance"},
            {"unit": "colreg-en-colreg_rule_27",
             "ref": "COLREG Rule 27(a)(ii)",
             "quote": "two balls or similar shapes in a vertical line"},
        ],
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
        "cites": [
            {"unit": "colreg-en-colreg_rule_27",
             "ref": "COLREG Rule 27(b)(ii)",
             "quote": "The highest and lowest of these shapes shall be balls and the middle one a diamond"},
        ],
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
        "cites": [
            {"unit": "colreg-en-colreg_rule_30",
             "ref": "COLREG Rule 30(d)(ii)",
             "quote": "three balls in a vertical line"},
        ],
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
        "cites": [
            {"unit": "colreg-en-colreg_rule_28",
             "ref": "COLREG Rule 28",
             "quote": "three all-round red lights in a vertical line, or a cylinder"},
        ],
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
        "cites": [
            {"unit": "colreg-en-colreg_rule_26",
             "ref": "COLREG Rule 26(c)(i)",
             "quote": "a shape consisting of two cones with apexes together in a vertical line"},
        ],
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
        "cites": [
            {"unit": "colreg-en-colreg_rule_24",
             "ref": "COLREG Rule 24(a)(v)",
             "quote": "a diamond shape where it can best be seen"},
        ],
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
        "cites": [
            {"unit": "colreg-en-colreg_rule_25",
             "ref": "COLREG Rule 25(e)",
             "quote": "a conical shape, apex downwards"},
        ],
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
        "cites": [
            {"unit": "colreg-en-colreg_rule_26",
             "ref": "COLREG Rule 26(c)(ii)",
             "quote": "a cone apex upwards in the direction of the gear"},
        ],
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
        "cites": [
            {"unit": "colreg-en-colreg_rule_30",
             "ref": "COLREG Rule 30(a)(i)",
             "quote": "in the fore part, an all-round white light or one ball"},
        ],
    },
    # Swiss inland balls are PAINTED, and the colour is the whole message — one of
    # the places the codes genuinely diverge, so these carry no COLREG citation and
    # are never offered to a maritime bank.
    {
        "key": "priority-green-ball",
        "shapes": [("ball", "#1a8f3c")],
        "title": "Un ballon vert",
        "source": {
            "unit": "oni-oni_art_27",
            "ref": "ONI art. 27 al. 1 let. b (RS 747.201.1)",
            "quote": "de jour, un ballon vert visible de tous les côtés",
        },
    },
    {
        "key": "trawling-white-ball",
        "shapes": [("ball", "#ffffff")],
        "title": "Un ballon blanc",
        "source": {
            "unit": "oni-oni_art_31",
            "ref": "ONI art. 31 al. 2 (RS 747.201.1)",
            "quote": "Les bateaux pêchant de jour à la traîne portent un ballon blanc",
        },
    },
    {
        "key": "fishing-yellow-ball",
        "shapes": [("ball", "#f2c317")],
        "title": "Un ballon jaune",
        "source": {
            "unit": "oni-oni_art_31",
            "ref": "ONI art. 31 al. 1 let. b (RS 747.201.1)",
            "quote": "de jour, un ballon jaune",
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
        "cites": [
            {"unit": "oni-oni_art_32",
             "ref": "ONI art. 32 al. 1 (RS 747.201.1)",
             "quote": "un panneau reproduisant la lettre «A» du Code "
                      "international de signaux"},
        ],
    },
]

# ── Sound-signals geometry ────────────────────────────────────────────────────
# A sound signal is a rhythm, so the figure is a timeline: each blast a bar whose
# WIDTH is its duration, separated by the pause the annex prescribes. This is not a
# stylisation — BinSchStrO Anlage 6 already draws its signals as ▬ and ▪ glyphs, and
# it states the durations behind them: "kurzer Ton: ein Ton von etwa einer Sekunde
# Dauer; langer Ton: ein Ton von etwa vier Sekunden Dauer. Die Pause zwischen zwei
# aufeinanderfolgenden Tönen beträgt etwa eine Sekunde." Drawing bars to scale says
# what the glyphs cannot: a long blast is FOUR times a short one, which is the whole
# discrimination in the four-question overtaking/harbour set (2 long + 1 short vs
# 2 long + 2 short vs 3 long + 1 short vs 3 long + 2 short).
#
# No second scale is printed on the figure. The inland code fixes the long blast at
# about four seconds and KVR Regel 32 allows four to six, so a numeric axis would
# claim a precision one of the two codes does not have. The ratio is common to both.
_SW, _SH = 340.0, 110.0
_SEC = 10.0            # px per second — the one scale the whole family shares
_BAR_TOP, _BAR_H = 42.0, 30.0
_TONE_S = {"short": 1.0, "long": 4.0, "very-short": 0.25}
_PAUSE = 1.0           # Anlage 6: about one second between consecutive tones
_GROUP_PAUSE = 2.6     # the wider air between two repetitions of a whole group
_TONE_INK = "#1f3a5f"
_RULE_INK = "#9aa8bd"


def _segments(pattern: list[str]) -> tuple[list[tuple[float, float]], float]:
    """Lay the pattern out once: ``[(x, width), …]`` plus the total width.

    Measuring and drawing walk the SAME list, so a timeline can never be centred by
    one rule and drawn by another. A ``gap`` token widens the pause that follows it
    instead of contributing a pause of its own — otherwise a group separator pays the
    inter-group air twice and the figure runs off its canvas."""
    out: list[tuple[float, float]] = []
    x, pause, first = 0.0, 0.0, True
    for tok in pattern:
        if tok == "gap":
            pause = _GROUP_PAUSE
            continue
        if not first:
            x += pause * _SEC
        w = _TONE_S[tok] * _SEC
        out.append((x, w))
        x += w
        first, pause = False, _PAUSE
    return out, x


def _pattern_width(pattern: list[str], repeat: bool) -> float:
    """Total drawn width, so the timeline can be centred on the shared canvas."""
    return _segments(pattern)[1] + (22.0 if repeat else 0.0)


def render_sound(pattern: list[str], title: str, repeat: bool = False,
                 source_ref: str = "") -> str:
    """A blast timeline, left to right.

    ``pattern`` is a list of ``short`` / ``long`` / ``very-short``, with ``gap`` as a
    separator where the source prescribes two groups ("zwei Gruppen von drei langen
    Tönen"). ``repeat`` appends a continuation mark for the signals the source says
    are repeated rather than given once."""
    if not pattern or any(t not in _TONE_S and t != "gap" for t in pattern):
        raise ValueError(f"bad blast pattern {pattern!r}; "
                         f"tones are {tuple(_TONE_S)} plus 'gap'")
    credit = (f"\n<!-- Generated figure, derived from {source_ref}; bar width = blast "
              f"duration, gap = the prescribed pause. Original artwork; project "
              f"licence (CC BY-SA 4.0), not a reproduction of any source figure. "
              f"{GENERATOR} -->" if source_ref else "")
    segs, _span = _segments(pattern)
    x0 = (_SW - _pattern_width(pattern, repeat)) / 2
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {_SW:g} {_SH:g}" '
        f'width="{_SW:g}" height="{_SH:g}" role="img" '
        f'aria-label="{_esc(title)}">{credit}',
        f'<title>{_esc(title)}</title>',
        f'<rect width="{_SW:g}" height="{_SH:g}" fill="#ffffff"/>',
        # the silence line the blasts sit on: it makes the pauses visible as pauses
        f'<line x1="14" y1="{_BAR_TOP + _BAR_H:g}" x2="{_SW - 14:g}" '
        f'y2="{_BAR_TOP + _BAR_H:g}" stroke="{_RULE_INK}" stroke-width="1.5"/>',
    ]
    for dx, w in segs:
        parts.append(f'<rect x="{x0 + dx:g}" y="{_BAR_TOP:g}" width="{w:g}" '
                     f'height="{_BAR_H:g}" rx="2" fill="{_TONE_INK}"/>')
    if repeat:
        end = x0 + _span
        for k in range(3):
            parts.append(f'<circle cx="{end + 8 + k * 7:g}" '
                         f'cy="{_BAR_TOP + _BAR_H - 3:g}" r="2" '
                         f'fill="{_TONE_INK}"/>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


# ── Give-way geometry ─────────────────────────────────────────────────────────
# A plan view, because right-of-way is the one family whose content IS a geometry:
# who is where, heading which way. The rules read as word puzzles ("the vessel which
# has the other on her own starboard side") and resolve instantly as pictures.
#
# Two conventions carry the whole diagram, and neither needs a caption — which
# matters, because one drawing serves four languages:
#
#   * the GIVE-WAY vessel gets a curved arrow: she is the one that alters.
#   * the STAND-ON vessel gets a straight arrow: she holds her course and speed.
#
# Nothing is colour-coded red/green, deliberately: those two colours already mean
# port and starboard everywhere else in this module, and reusing them for roles
# would collide with the sidelight convention the learner is being taught.
_GW, _GH = 200.0, 200.0
_WATER = "#eaf1f8"
_HULL_GIVE = "#1f3a5f"      # the vessel that must act, drawn solid
_HULL_STAND = "#ffffff"     # the vessel that must not, drawn open
_HULL_EDGE = "#1f3a5f"
_ARROW = "#5b6b80"
_SECTOR = "#f4c542"


def _rot(x: float, y: float, cx: float, cy: float, deg: float) -> tuple[float, float]:
    """Rotate a point about a centre. Heading 0 points up the page (north)."""
    import math
    a = math.radians(deg)
    dx, dy = x - cx, y - cy
    return (cx + dx * math.cos(a) - dy * math.sin(a),
            cy + dx * math.sin(a) + dy * math.cos(a))


def _hull(cx: float, cy: float, hdg: float, give_way: bool) -> str:
    """A hull seen from above, bow along ``hdg``. Length 44, beam 18 — enough to read
    the heading at card size without becoming a picture of a particular boat."""
    pts = [(cx, cy - 22), (cx + 9, cy - 6), (cx + 9, cy + 20), (cx - 9, cy + 20),
           (cx - 9, cy - 6)]
    got = " ".join(f"{px:.1f},{py:.1f}"
                   for px, py in (_rot(x, y, cx, cy, hdg) for x, y in pts))
    fill = _HULL_GIVE if give_way else _HULL_STAND
    return (f'<polygon points="{got}" fill="{fill}" stroke="{_HULL_EDGE}" '
            f'stroke-width="2" stroke-linejoin="round"/>')


def _course_arrow(cx: float, cy: float, hdg: float, give_way: bool) -> str:
    """Straight ahead for the stand-on vessel (hold course), curving to starboard for
    the one that must keep out of the way (she is the one that alters)."""
    if not give_way:
        tip = _rot(cx, cy - 54, cx, cy, hdg)
        base = _rot(cx, cy - 28, cx, cy, hdg)
        l = _rot(cx - 5, cy - 44, cx, cy, hdg)
        r = _rot(cx + 5, cy - 44, cx, cy, hdg)
        return (f'<line x1="{base[0]:.1f}" y1="{base[1]:.1f}" x2="{tip[0]:.1f}" '
                f'y2="{tip[1]:.1f}" stroke="{_ARROW}" stroke-width="2.5"/>'
                f'<polygon points="{tip[0]:.1f},{tip[1]:.1f} {l[0]:.1f},{l[1]:.1f} '
                f'{r[0]:.1f},{r[1]:.1f}" fill="{_ARROW}"/>')
    start = _rot(cx, cy - 26, cx, cy, hdg)
    ctrl = _rot(cx + 4, cy - 44, cx, cy, hdg)
    end = _rot(cx + 30, cy - 50, cx, cy, hdg)
    tipl = _rot(cx + 22, cy - 56, cx, cy, hdg)
    tipr = _rot(cx + 24, cy - 40, cx, cy, hdg)
    return (f'<path d="M{start[0]:.1f},{start[1]:.1f} Q{ctrl[0]:.1f},{ctrl[1]:.1f} '
            f'{end[0]:.1f},{end[1]:.1f}" fill="none" stroke="{_ARROW}" '
            f'stroke-width="2.5"/>'
            f'<polygon points="{end[0]:.1f},{end[1]:.1f} {tipl[0]:.1f},{tipl[1]:.1f} '
            f'{tipr[0]:.1f},{tipr[1]:.1f}" fill="{_ARROW}"/>')


def _boom(cx: float, cy: float, hdg: float, side: str) -> str:
    """The mainsail boom, which is what Rule 12(b) reads the wind off: the windward
    side is the one OPPOSITE the mainsail. Drawing the boom is therefore drawing the
    tack, without a word of explanation."""
    dx = -30 if side == "port" else 30
    mast = _rot(cx, cy - 8, cx, cy, hdg)
    clew = _rot(cx + dx, cy + 20, cx, cy, hdg)
    belly = _rot(cx + dx * 0.45, cy + 2, cx, cy, hdg)
    # the sail as seen from above: a curved sliver from the mast to the clew, on the
    # side the boom is out. Rule 12(b) reads the wind off exactly this — the windward
    # side is the one opposite the mainsail — so drawing it IS drawing the tack.
    return (f'<path d="M{mast[0]:.1f},{mast[1]:.1f} Q{belly[0]:.1f},{belly[1]:.1f} '
            f'{clew[0]:.1f},{clew[1]:.1f}" fill="none" stroke="{_HULL_EDGE}" '
            f'stroke-width="6" stroke-linecap="round" stroke-opacity="0.55"/>'
            f'<circle cx="{mast[0]:.1f}" cy="{mast[1]:.1f}" r="3" '
            f'fill="{_HULL_EDGE}"/>')


def _stern_sector(cx: float, cy: float, hdg: float) -> str:
    """The 135° arc astern — Rule 13(b) defines overtaking as coming up from more than
    22.5° abaft the beam, which is exactly the arc in which only the sternlight shows.
    Shading it turns a bearing rule into a place on the water."""
    import math
    r = 78.0
    out = []
    for edge in (-67.5, 67.5):
        px, py = _rot(cx, cy + r, cx, cy, hdg + edge)
        out.append((px, py))
    big = 0
    return (f'<path d="M{cx:.1f},{cy:.1f} L{out[0][0]:.1f},{out[0][1]:.1f} '
            f'A{r:g},{r:g} 0 {big} 1 {out[1][0]:.1f},{out[1][1]:.1f} Z" '
            f'fill="{_SECTOR}" fill-opacity="0.30" stroke="{_SECTOR}" '
            f'stroke-width="1.5"/>') if not math.isnan(r) else ""


def _river() -> str:
    """Two banks and a flow arrow. Without the current on the page there is nothing
    to tell a montant from an avalant, and the whole inland meeting rule is about
    which of the two is which."""
    return (f'<rect x="0" y="0" width="26" height="{_GH:g}" fill="#dfe7d8"/>'
            f'<rect x="{_GW - 26:g}" y="0" width="26" height="{_GH:g}" '
            f'fill="#dfe7d8"/>'
            f'<line x1="26" y1="0" x2="26" y2="{_GH:g}" stroke="#b9c8ab" '
            f'stroke-width="2"/>'
            f'<line x1="{_GW - 26:g}" y1="0" x2="{_GW - 26:g}" y2="{_GH:g}" '
            f'stroke="#b9c8ab" stroke-width="2"/>'
            # flow: downstream is down the page
            f'<line x1="13" y1="64" x2="13" y2="126" stroke="#8fa87e" '
            f'stroke-width="2.5"/>'
            f'<polygon points="13,138 7,124 19,124" fill="#8fa87e"/>'
            f'<line x1="{_GW - 13:g}" y1="64" x2="{_GW - 13:g}" y2="126" '
            f'stroke="#8fa87e" stroke-width="2.5"/>'
            f'<polygon points="{_GW - 13:g},138 {_GW - 19:g},124 '
            f'{_GW - 7:g},124" fill="#8fa87e"/>')


def render_giveway(boats: list[dict], title: str, wind: bool = False,
                   sector_on: int | None = None, source_ref: str = "",
                   river: bool = False) -> str:
    """A plan view of an encounter. ``boats`` are dicts with x, y, hdg, role
    ('give-way' | 'stand-on') and optional boom side for sailing vessels."""
    credit = (f"\n<!-- Generated figure, derived from {source_ref}. Solid hull with a "
              f"curving arrow = the vessel that keeps out of the way; open hull with a "
              f"straight arrow = the vessel that holds course. Original artwork; "
              f"project licence (CC BY-SA 4.0). {GENERATOR} -->" if source_ref else "")
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {_GW:g} {_GH:g}" '
        f'width="{_GW:g}" height="{_GH:g}" role="img" '
        f'aria-label="{_esc(title)}">{credit}',
        f'<title>{_esc(title)}</title>',
        f'<rect width="{_GW:g}" height="{_GH:g}" fill="{_WATER}"/>',
    ]
    if river:
        parts.append(_river())
    if wind:
        # Wind down the page, so "the wind on the port side" is readable off the boom.
        parts.append(f'<line x1="{_GW / 2:g}" y1="8" x2="{_GW / 2:g}" y2="34" '
                     f'stroke="{_ARROW}" stroke-width="2" stroke-dasharray="4 3"/>')
        parts.append(f'<polygon points="{_GW / 2:g},40 {_GW / 2 - 5:g},30 '
                     f'{_GW / 2 + 5:g},30" fill="{_ARROW}"/>')
    if sector_on is not None:
        b = boats[sector_on]
        parts.append(_stern_sector(b["x"], b["y"], b["hdg"]))
    for b in boats:
        give = b["role"] == "give-way"
        parts.append(_course_arrow(b["x"], b["y"], b["hdg"], give))
        parts.append(_hull(b["x"], b["y"], b["hdg"], give))
        if b.get("boom"):
            parts.append(_boom(b["x"], b["y"], b["hdg"], b["boom"]))
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


# ── Nav-lights: the spec ──────────────────────────────────────────────────
# ``column`` is top-to-bottom on the centreline; ``sidelights`` says the vessel is
# making way through the water (several Rules prescribe the identity lights always
# and the sidelights only "bei Fahrt durchs Wasser" — that difference is the whole
# question in more than one pair below).
#
# Where a Rule stacks a group of lights on TOP of another group without saying which
# sits where, no diagram is drawn. Regel 30 d) is the case: a vessel aground shows
# the anchor light(s) of a) or b) *plus* two red all-round lights "dort, wo sie am
# besten gesehen werden können" — the law fixes the order inside each group and is
# silent between them. Anlage I §2 f) i) settles the same question for masthead
# lights (they top everything), which is why the vessels below can be drawn at all.
# Frage 105 and Frage 107 (aground, under and over 50 m) therefore stay
# unillustrated rather than have us invent a stacking order.
_UNPRESCRIBED = ("aground: Regel 30 d) fixes the order within each group of lights "
                 "but not between the anchor lights and the two red all-round "
                 "lights, so no arrangement can be drawn from the source alone")

NAV_LIGHTS: list[dict] = [
    {
        "key": "power-driven-under-50m",
        "column": ["white"], "sidelights": True,
        "title": "Ein weißes Licht oben, grünes Licht links, rotes Licht rechts",
        "source": {
            "unit": "kvr-de-seestro_1972_regel_23",
            "ref": "SeeStrO 1972 Regel 23 Buchstabe a",
            "quote": "ein Topplicht vorn; ii) ein zweites Topplicht achterlicher "
                     "und höher als das vordere; ein Fahrzeug von weniger als 50 "
                     "Meter Länge kann ein solches Licht führen, ist jedoch nicht "
                     "dazu verpflichtet",
        },
        "cites": [
            {"unit": "colreg-en-colreg_rule_23",
             "ref": "COLREG Rule 23(a)",
             "quote": "a masthead light forward; (ii) a second masthead light "
                      "abaft of and higher than the forward one; except that a "
                      "vessel of less than 50 meters in length shall not be"},
        ],
    },
    {
        "key": "power-driven-over-50m",
        "column": ["white", "white"], "sidelights": True,
        "title": "Zwei weiße Lichter übereinander, grünes Licht links, rotes rechts",
        "source": {
            "unit": "kvr-de-seestro_1972_regel_23",
            "ref": "SeeStrO 1972 Regel 23 Buchstabe a Ziffer ii",
            "quote": "ein zweites Topplicht achterlicher und höher als das vordere",
        },
        "cites": [
            {"unit": "colreg-en-colreg_rule_23",
             "ref": "COLREG Rule 23(a)(ii)",
             "quote": "a second masthead light abaft of and higher than the forward one"},
        ],
    },
    {
        "key": "nuc-two-red",
        "column": ["red", "red"], "sidelights": False,
        "title": "Zwei rote Lichter senkrecht übereinander",
        "source": {
            "unit": "kvr-de-seestro_1972_regel_27",
            "ref": "SeeStrO 1972 Regel 27 Buchstabe a Ziffer i",
            "quote": "zwei rote Rundumlichter senkrecht übereinander",
        },
        "cites": [
            {"unit": "colreg-en-colreg_rule_27",
             "ref": "COLREG Rule 27(a)(i)",
             "quote": "two all-round red lights in a vertical line"},
        ],
    },
    {
        "key": "nuc-two-red-making-way",
        "column": ["red", "red"], "sidelights": True,
        "title": "Zwei rote Lichter übereinander, grünes Licht links, rotes rechts",
        "source": {
            "unit": "kvr-de-seestro_1972_regel_27",
            "ref": "SeeStrO 1972 Regel 27 Buchstabe a Ziffer iii",
            "quote": "bei Fahrt durchs Wasser zusätzlich zu den unter diesem "
                     "Buchstaben vorgeschriebenen Lichtern Seitenlichter und ein "
                     "Hecklicht",
        },
        "cites": [
            {"unit": "colreg-en-colreg_rule_27",
             "ref": "COLREG Rule 27(a)(iii)",
             "quote": "when making way through the water, in addition to the "
                      "lights prescribed in this paragraph, sidelights and a "
                      "sternlight"},
        ],
    },
    {
        "key": "ram-red-white-red",
        "column": ["red", "white", "red"], "sidelights": False,
        "title": "Rotes, weißes, rotes Licht senkrecht übereinander",
        "source": {
            "unit": "kvr-de-seestro_1972_regel_27",
            "ref": "SeeStrO 1972 Regel 27 Buchstabe b Ziffer i",
            "quote": "Das obere und das untere Licht müssen rot, das mittlere muß "
                     "weiß sein",
        },
        "cites": [
            {"unit": "colreg-en-colreg_rule_27",
             "ref": "COLREG Rule 27(b)(i)",
             "quote": "The highest and lowest of these lights shall be red and the middle light shall be white"},
        ],
    },
    {
        "key": "ram-making-way",
        "column": ["white", "red", "white", "red"], "sidelights": True,
        "title": "Weißes Licht oben, darunter rot-weiß-rot, grünes Licht links, "
                 "rotes rechts",
        "source": {
            "unit": "kvr-de-seestro_1972_regel_27",
            "ref": "SeeStrO 1972 Regel 27 Buchstabe b Ziffer iii",
            "quote": "bei Fahrt durchs Wasser zusätzlich zu den unter Ziffer i "
                     "vorgeschriebenen Lichtern ein Topplicht oder mehrere "
                     "Topplichter sowie Seitenlichter und ein Hecklicht",
        },
    },
    {
        "key": "constrained-by-draught",
        "column": ["white", "white", "red", "red", "red"], "sidelights": True,
        "title": "Zwei weiße Lichter oben, darunter drei rote, grünes Licht links, "
                 "rotes rechts",
        "source": {
            "unit": "kvr-de-seestro_1972_regel_28",
            "ref": "SeeStrO 1972 Regel 28",
            "quote": "drei rote Rundumlichter senkrecht übereinander",
        },
    },
    {
        "key": "trawler-making-way",
        "column": ["white", "green", "white"], "sidelights": True,
        "title": "Weißes Licht oben, darunter grün über weiß, grünes Licht links, "
                 "rotes rechts",
        "source": {
            "unit": "kvr-de-seestro_1972_regel_26",
            "ref": "SeeStrO 1972 Regel 26 Buchstabe b",
            "quote": "zwei Rundumlichter senkrecht übereinander, das obere grün und "
                     "das untere weiß",
        },
        "cites": [
            {"unit": "colreg-en-colreg_rule_26",
             "ref": "COLREG Rule 26(b)(i)",
             "quote": "two all-round lights in a vertical line, the upper being green and the lower white"},
        ],
    },
    {
        "key": "fishing-not-trawling",
        "column": ["red", "white"], "sidelights": False,
        "title": "Rotes Licht über weißem Licht",
        "source": {
            "unit": "kvr-de-seestro_1972_regel_26",
            "ref": "SeeStrO 1972 Regel 26 Buchstabe c Ziffer i",
            "quote": "zwei Rundumlichter senkrecht übereinander, das obere rot und "
                     "das untere weiß",
        },
        "cites": [
            {"unit": "colreg-en-colreg_rule_26",
             "ref": "COLREG Rule 26(c)(i)",
             "quote": "two all-round lights in a vertical line, the upper being red and the lower white"},
        ],
    },
    {
        "key": "anchored-two-lights",
        "column": ["white", "white"], "sidelights": False,
        "title": "Zwei weiße Lichter senkrecht übereinander",
        "source": {
            "unit": "kvr-de-seestro_1972_anlage_i",
            "ref": "SeeStrO 1972 Anlage I §2 Buchstabe k (mit Regel 30 Buchstabe a)",
            "quote": "Werden zwei Ankerlichter geführt, so muß das in Regel 30 "
                     "Buchstabe a Ziffer i vorgeschriebene vordere mindestens 4,5 "
                     "Meter höher als das hintere angebracht sein",
        },
        "cites": [
            {"unit": "colreg-en-colreg_rule_30",
             "ref": "COLREG Rule 30(a)(ii)",
             "quote": "at or near the stern and at a lower level than the light prescribed"},
        ],
    },
]

# ── Sound-signals: the spec ───────────────────────────────────────────────────
# Two regimes, kept apart on purpose. The inland signals come from BinSchStrO
# Anlage 6, which tabulates every one of them with its own ▬/▪ glyphs; the sea
# signals from SeeSchStrO Anlage I/II and the KVR. The same rhythm can mean
# different things under the two codes, so a diagram is only ever attached to a
# question from the catalogue whose code it was drawn from.
SOUND_SIGNALS: list[dict] = [
    # ── inland (BinSchStrO Anlage 6) ──
    {
        "key": "inland-turn-to-starboard",
        "pattern": ["long", "short"],
        "title": "Ein langer Ton, ein kurzer Ton",
        "source": {
            "unit": "binschstro-de-binschstro_2012_anlage_6",
            "ref": "BinSchStrO 2012 Anlage 6 Abschnitt D (§ 6.13 Nummer 2 Buchstabe a)",
            "quote": "1 langer Ton, „Ich wende über Steuerbord“",
        },
        "cites": [
            {"unit": "code_transports-code_des_transports_art_a42415314",
             "ref": "Code des transports, art. A4241-53-14 (RGP)",
             "quote": "Un son prolongé suivi d'un son bref s'il veut virer sur tribord"},
        ],
    },
    {
        "key": "inland-turn-to-port",
        "pattern": ["long", "short", "short"],
        "title": "Ein langer Ton, zwei kurze Töne",
        "source": {
            "unit": "binschstro-de-binschstro_2012_anlage_6",
            "ref": "BinSchStrO 2012 Anlage 6 Abschnitt D (§ 6.13 Nummer 2 Buchstabe b)",
            "quote": "1 langer Ton, „Ich wende über Backbord“",
        },
        "cites": [
            {"unit": "code_transports-code_des_transports_art_a42415314",
             "ref": "Code des transports, art. A4241-53-14 (RGP)",
             "quote": "Un son prolongé suivi de deux sons brefs s'il veut virer sur bâbord"},
        ],
    },
    {
        "key": "inland-overtake-to-starboard",
        "pattern": ["long", "long", "short"],
        "title": "Zwei lange Töne, ein kurzer Ton",
        "source": {
            "unit": "binschstro-de-binschstro_2012_anlage_6",
            "ref": "BinSchStrO 2012 Anlage 6 Abschnitt C (§ 6.10 Nummer 2 Buchstabe b)",
            "quote": "2 lange Töne, „Ich will auf Ihrer Steuerbordseite überholen“",
        },
        "cites": [
            {"unit": "code_transports-code_des_transports_art_a42415311",
             "ref": "Code des transports, art. A4241-53-11 (RGP)",
             "quote": "Deux sons prolongés suivis d'un son bref"},
        ],
    },
    {
        "key": "inland-overtake-to-port",
        "pattern": ["long", "long", "short", "short"],
        "title": "Zwei lange Töne, zwei kurze Töne",
        "source": {
            "unit": "binschstro-de-binschstro_2012_anlage_6",
            "ref": "BinSchStrO 2012 Anlage 6 Abschnitt C (§ 6.10 Nummer 2 Buchstabe a)",
            "quote": "2 lange Töne, „Ich will auf Ihrer Backbordseite überholen“",
        },
        "cites": [
            {"unit": "code_transports-code_des_transports_art_a42415311",
             "ref": "Code des transports, art. A4241-53-11 (RGP)",
             "quote": "Deux sons prolongés suivis de deux sons brefs s'il veut dépasser par bâbord"},
        ],
    },
    {
        "key": "inland-harbour-turn-starboard",
        "pattern": ["long", "long", "long", "short"],
        "title": "Drei lange Töne, ein kurzer Ton",
        "source": {
            "unit": "binschstro-de-binschstro_2012_anlage_6",
            "ref": "BinSchStrO 2012 Anlage 6 Abschnitt E (§ 6.16 Nummer 2 Satz 1 "
                   "Buchstabe a)",
            "quote": "3 lange Töne, „Ich will meinen Kurs nach Steuerbord richten“",
        },
        "cites": [
            {"unit": "code_transports-code_des_transports_art_a42415317",
             "ref": "Code des transports, art. A4241-53-17 (RGP)",
             "quote": "Trois sons prolongés suivis d'un son bref"},
        ],
    },
    {
        "key": "inland-harbour-turn-port",
        "pattern": ["long", "long", "long", "short", "short"],
        "title": "Drei lange Töne, zwei kurze Töne",
        "source": {
            "unit": "binschstro-de-binschstro_2012_anlage_6",
            "ref": "BinSchStrO 2012 Anlage 6 Abschnitt E (§ 6.16 Nummer 2 Satz 1 "
                   "Buchstabe b)",
            "quote": "3 lange Töne, „Ich will meinen Kurs nach Backbord richten“",
        },
        "cites": [
            {"unit": "code_transports-code_des_transports_art_a42415317",
             "ref": "Code des transports, art. A4241-53-17 (RGP)",
             "quote": "Trois sons prolongés suivis de de"},
        ],
    },
    {
        "key": "inland-stay-away",
        "pattern": ["short", "long", "short", "long"], "repeat": True,
        "title": "Abwechselnd ein kurzer und ein langer Ton, ununterbrochen "
                 "wiederholt",
        "source": {
            "unit": "binschstro-de-binschstro_2012_anlage_6",
            "ref": "BinSchStrO 2012 Anlage 6 Abschnitt A (§ 8.09 Nummer 2)",
            "quote": "ununterbrochene Wiederholung abwech- selnd eines kurzen und "
                     "eines langen Tones",
        },
    },
    # ── sea (SeeSchStrO / KVR) ──
    {
        "key": "sea-general-danger",
        "pattern": ["long", "short", "short", "short", "short", "gap",
                    "long", "short", "short", "short", "short"],
        "title": "Zwei Gruppen von je einem langen und vier kurzen Tönen",
        "source": {
            "unit": "seeschstro-de-seeschstro_1971_anlage_ii",
            "ref": "SeeSchStrO 1971 Anlage II Nummer 2.1",
            "quote": "ein langer Ton, vier kurze Töne",
        },
    },
    {
        "key": "sea-bridge-lock-closed",
        "pattern": ["short", "short", "short", "short"],
        "title": "Vier kurze Töne",
        "source": {
            "unit": "seeschstro-de-seeschstro_1971_anlage_i",
            "ref": "SeeSchStrO 1971 Anlage I Abschnitt II C.2",
            "quote": "Schleuse kann vorübergehend nicht geöffnet werden) vier "
                     "kurze Töne",
        },
    },
    {
        "key": "sea-official-vessel-stop",
        "pattern": ["short", "long", "short", "short"],
        "title": "Ein kurzer Ton, ein langer Ton, zwei kurze Töne",
        "source": {
            "unit": "seeschstro-de-seeschstro_1971_anlage_i",
            "ref": "SeeSchStrO 1971 Anlage I Abschnitt II C.1",
            "quote": "Anhalten von einem Fahrzeug des öffentlichen Dienstes: ein "
                     "kurzer Ton, ein langer Ton, zwei kurze Töne",
        },
    },
    {
        "key": "sea-waterway-closed",
        "pattern": ["long", "long", "long", "gap", "long", "long", "long"],
        "title": "Zwei Gruppen von je drei langen Tönen",
        "source": {
            "unit": "seeschstro-de-seeschstro_1971_anlage_i",
            "ref": "SeeSchStrO 1971 Anlage I Abschnitt II C.4",
            "quote": "Sperrung der Seeschiffahrtsstraße zwei Gruppen von drei "
                     "langen Tönen",
        },
    },
    {
        "key": "sea-anchored-warning",
        "pattern": ["short", "long", "short"],
        "title": "Ein kurzer, ein langer, ein kurzer Ton",
        "source": {
            "unit": "kvr-de-seestro_1972_regel_35",
            "ref": "SeeStrO 1972 Regel 35 Buchstabe g",
            "quote": "drei aufeinanderfolgende Töne - kurz, lang, kurz -",
        },
        "cites": [
            {"unit": "colreg-en-colreg_rule_35",
             "ref": "COLREG Rule 35(g)",
             "quote": "three blasts in succession, namely one short, one prolonged and one short blast"},
        ],
    },
    {
        "key": "sea-sos",
        "pattern": ["short", "short", "short", "gap", "long", "long", "long",
                    "gap", "short", "short", "short"],
        "title": "Drei kurze, drei lange, drei kurze Töne",
        "source": {
            "unit": "kvr-de-seestro_1972_anlage_iv",
            "ref": "SeeStrO 1972 Anlage IV Nummer 1 Buchstabe d",
            "quote": "das durch eine beliebige Signalart gegebene Morsesignal "
                     "...---... (SOS)",
        },
    },
]

# ── Which law lets a diagram reach which bank ─────────────────────────────────
# A drawing is geometry, so the SAME picture is valid under several codes — but the
# citation is not transferable. Telling a French learner that his day shape comes
# from "SeeStrO 1972 Regel 27" would be asserting German law at him, and worse, the
# codes genuinely diverge (Swiss inland balls are coloured; COLREG's are black).
#
# So every diagram carries one citation PER REGIME, each verified against that
# regime's own KB, and a diagram may only be offered to a bank whose regime it can
# cite. The regime is the KB unit-id prefix — no extra field to keep in sync.
#
# fr_cotiere reads COLREG because RIPAM *is* COLREG as enacted in France (the regime
# tree in docs/scope.md records it as `implements`), which is already how the
# maritime concept cards cite themselves: "COLREG 1972 / RIPAM".
BANK_REGIMES: dict[str, tuple[str, ...]] = {
    "de": ("kvr", "seeschstro", "binschstro"),
    "int": ("colreg",),
    "fr_cotiere": ("colreg",),
    "fr_eaux_interieures": ("code_transports",),
    "ch": ("oni", "rnl"),
}
BANK_KB = {"de": "kb.de.sqlite", "int": "kb.int.sqlite",
           "fr_cotiere": "kb.int.sqlite", "ch": "kb.ch.sqlite",
           "fr_eaux_interieures": "kb.fr.sqlite"}


def regime_of(unit: str) -> str:
    """The code a KB unit belongs to, read off its id prefix (``colreg-en-…``)."""
    return (unit or "").split("-", 1)[0]


def citations(d: dict) -> list[dict]:
    """Every citation for a diagram: the article it was drawn from, plus the
    equivalent article in each other code that prescribes the same figure."""
    return [d["source"], *d.get("cites", [])]


def keys_for_bank(bank_id: str) -> set[str]:
    """Diagram keys this bank's own law can account for. A diagram with no citation
    in the bank's regime is simply not offered there — silence beats a picture the
    learner's code does not actually prescribe."""
    allowed = set(BANK_REGIMES.get(bank_id, ()))
    return {d["key"] for d in DIAGRAMS
            if any(regime_of(c["unit"]) in allowed for c in citations(d))}


def figures_for_bank_cards(bank_id: str) -> list[str]:
    """Every diagram key any of this bank's concept cards can show — what the web
    bundler must copy alongside ``concepts.<lang>.json``."""
    out: list[str] = []
    for family in FAMILIES:
        out.extend(figures_for(family, bank_id))
    return out


def figures_for(principle: str, bank_id: str) -> list[str]:
    """The vocabulary strip for one concept card: every diagram of this principle's
    family that the bank's own code prescribes, in spec order.

    Derived rather than hand-listed, so adding a diagram lights it up on every card
    entitled to it and no list can quietly fall out of date. Returns [] when the
    bank's law does not cover the family, which is the graceful case — the card
    simply shows no strip."""
    ok = keys_for_bank(bank_id)
    return [d["key"] for d in DIAGRAMS
            if d["family"] == principle and d["key"] in ok]


# ── Give-way: the spec ────────────────────────────────────────────────────────
# These live on concept cards only. Every one of them shows WHO gives way, which is
# the answer to the questions they illustrate — so unlike the other families they
# must never be attached to a stem, and none appears in ASSIGNMENTS.
GIVE_WAY: list[dict] = [
    {
        "key": "meeting-head-on",
        "boats": [{"x": 86, "y": 166, "hdg": 0, "role": "give-way"},
                  {"x": 114, "y": 34, "hdg": 180, "role": "give-way"}],
        "title": "Deux bateaux à moteur face à face ; chacun vient sur tribord",
        "source": {
            "unit": "colreg-en-colreg_rule_14",
            "ref": "COLREG Rule 14(a)",
            "quote": "each shall alter her course to starboard so that each shall "
                     "pass on the port side of the other",
        },
        "cites": [
            {"unit": "code_transports-code_des_transports_art_a4241536",
             "ref": "Code des transports, art. A4241-53-6 ch. 1 (RGP)",
             "quote": "chacun doit venir sur tribord pour passer à bâbord "
                      "de l'autre"},
        ],
    },
    {
        "key": "crossing-give-way-to-starboard",
        "boats": [{"x": 74, "y": 150, "hdg": 0, "role": "give-way"},
                  {"x": 150, "y": 74, "hdg": 270, "role": "stand-on"}],
        "title": "Routes qui se croisent : celui qui voit l’autre sur tribord s’écarte",
        "source": {
            "unit": "colreg-en-colreg_rule_15",
            "ref": "COLREG Rule 15",
            "quote": "the vessel which has the other on her own starboard side shall "
                     "keep out of the way",
        },
        "cites": [
            {"unit": "code_transports-code_des_transports_art_a4241535",
             "ref": "Code des transports, art. A4241-53-5 ch. 1 (RGP)",
             "quote": "le bateau qui voit l'autre bateau tribord "
                      "s'écarte de la route de celui-ci"},
        ],
    },
    {
        "key": "overtaking-stern-sector",
        "boats": [{"x": 100, "y": 78, "hdg": 0, "role": "stand-on"},
                  {"x": 118, "y": 158, "hdg": 350, "role": "give-way"}],
        "sector_on": 0,
        "title": "Rattrapage : venir de plus de 22,5° sur l’arrière du travers",
        "source": {
            "unit": "colreg-en-colreg_rule_13",
            "ref": "COLREG Rule 13(a)-(b)",
            "quote": "coming up with another vessel from a direction more than 22.5 "
                     "degrees abaft her beam",
        },
    },
    {
        "key": "sailing-opposite-tacks",
        "boats": [{"x": 56, "y": 142, "hdg": 25, "role": "give-way",
                   "boom": "stbd"},
                  {"x": 146, "y": 138, "hdg": 335, "role": "stand-on",
                   "boom": "port"}],
        "wind": True,
        "title": "Deux voiliers, vent de bordées différentes",
        "source": {
            "unit": "colreg-en-colreg_rule_12",
            "ref": "COLREG Rule 12(a)(i)",
            "quote": "when each has the wind on a different side, the vessel which "
                     "has the wind on the port side shall keep out of the way",
        },
    },
    {
        "key": "inland-upstream-yields",
        "boats": [{"x": 84, "y": 164, "hdg": 0, "role": "give-way"},
                  {"x": 118, "y": 38, "hdg": 180, "role": "stand-on"}],
        "river": True,
        "title": "Rencontre en rivière : le montant laisse la route à l’avalant",
        "source": {
            "unit": "binschstro-de-binschstro_2012__604",
            "ref": "BinSchStrO 2012 § 6.04 Nummer 1",
            "quote": "muss der Bergfahrer unter Berücksichtigung der örtlichen "
                     "Umstände und des übrigen Verkehrs dem Talfahrer einen "
                     "geeigneten Weg freilassen",
        },
        "cites": [
            {"unit": "code_transports-code_des_transports_art_a4241536",
             "ref": "Code des transports, art. A4241-53-6 ch. 2 (RGP)",
             "quote": "les montants doivent, compte tenu des circonstances locales et "
                      "des mouvements des autres bateaux, réserver aux avalants une "
                      "route appropriée"},
        ],
    },
    {
        "key": "keep-to-starboard-side",
        "boats": [{"x": 86, "y": 166, "hdg": 0, "role": "give-way"},
                  {"x": 114, "y": 34, "hdg": 180, "role": "give-way"}],
        "title": "En cas de rencontre, chacun tient sa droite",
        "source": {
            "unit": "oni-oni_art_63",
            "ref": "ONI art. 63 al. 2 (RS 747.201.1)",
            "quote": "En cas de rencontre, les bateaux doivent tenir leur droite",
        },
    },
]

DIAGRAMS: list[dict] = ([{**d, "family": "day-shapes"} for d in DAY_SHAPES]
                        + [{**d, "family": "nav-lights"} for d in NAV_LIGHTS]
                        + [{"repeat": False, **d, "family": "sound-signals"}
                           for d in SOUND_SIGNALS]
                        + [{"wind": False, "sector_on": None, "river": False,
                            **d, "family": "give-way"} for d in GIVE_WAY])
BY_KEY: dict[str, dict] = {d["key"]: d for d in DIAGRAMS}


def path_for(key: str) -> str:
    """Repo-relative path of a rendered diagram (the value stored in Question.image)."""
    return f"{OUT_DIR}/{key}.svg".replace(os.sep, "/")


def render_one(d: dict) -> str:
    """Render one spec entry through its family's renderer."""
    if d["family"] == "day-shapes":
        return render(d["shapes"], d["title"], d["source"]["ref"])
    if d["family"] == "nav-lights":
        return render_lights(d["column"], d["sidelights"], d["title"],
                             d["source"]["ref"])
    if d["family"] == "sound-signals":
        return render_sound(d["pattern"], d["title"], d["repeat"],
                            d["source"]["ref"])
    if d["family"] == "give-way":
        return render_giveway(d["boats"], d["title"], d["wind"], d["sector_on"],
                              d["source"]["ref"], d["river"])
    raise ValueError(f"unknown family {d['family']!r}; expected one of {FAMILIES}")


def render_all(root: str = ".") -> dict:
    """Render every diagram to ``data/assets/diagrams/``. Deterministic: same spec in,
    byte-identical files out, so re-running never churns the tree."""
    out = os.path.join(root, OUT_DIR)
    os.makedirs(out, exist_ok=True)
    written = 0
    for d in DIAGRAMS:
        svg = render_one(d)
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
_DEICTIC = ("diese ", "dieses ", "diesen ", "folgende ", "folgendes ", "folgenden ",
            "this ", "these ", "the following ", "ce ", "ces ", "cette ",
            "questo ", "questi ", "queste ")

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

    # nav-lights. Note the pairs that differ ONLY by the sidelights: Frage 97/98
    # (not under command, underway vs making way) and Frage 102/103 (restricted in
    # her ability to manoeuvre). The Rules prescribe the identity lights always and
    # the sidelights only "bei Fahrt durchs Wasser", so the two pictures teach that
    # distinction better than any sentence could.
    {"bank": "de", "catalogue": "SBF See", "ref": "Frage 91",
     "expect": "weniger als 50 m", "key": "power-driven-under-50m",
     "why": "deictic"},
    {"bank": "de", "catalogue": "SBF See", "ref": "Frage 92",
     "expect": "50 und mehr Meter", "key": "power-driven-over-50m",
     "why": "deictic"},
    {"bank": "de", "catalogue": "SBF See", "ref": "Frage 97",
     "expect": "manövrierunfähiges", "key": "nuc-two-red", "why": "deictic"},
    {"bank": "de", "catalogue": "SBF See", "ref": "Frage 98",
     "expect": "manövrierunfähiges Fahrzeug mit Fahrt",
     "key": "nuc-two-red-making-way", "why": "deictic"},
    {"bank": "de", "catalogue": "SBF See", "ref": "Frage 102",
     "expect": "manövrierbehindertes", "key": "ram-red-white-red", "why": "deictic"},
    {"bank": "de", "catalogue": "SBF See", "ref": "Frage 103",
     "expect": "manövrierbehindertes Fahrzeug mit Fahrt", "key": "ram-making-way",
     "why": "deictic"},
    {"bank": "de", "catalogue": "SBF See", "ref": "Frage 108",
     "expect": "tiefgangbehindertes", "key": "constrained-by-draught",
     "why": "deictic"},
    {"bank": "de", "catalogue": "SBF See", "ref": "Frage 110",
     "expect": "Trawler", "key": "trawler-making-way", "why": "deictic"},
    {"bank": "de", "catalogue": "SBF See", "ref": "Frage 111",
     "expect": "nicht trawlt", "key": "fishing-not-trawling", "why": "deictic"},
    {"bank": "de", "catalogue": "SBF See", "ref": "Frage 115",
     "expect": "vor Anker", "key": "anchored-two-lights", "why": "deictic"},

    # sound-signals. The four inland questions below are one family whose entire
    # difficulty is counting: 2 long + 1 short, 2 long + 2 short, 3 long + 1 short,
    # 3 long + 2 short. Drawn to scale they stop being four things to memorise.
    {"bank": "de", "catalogue": "SBF Binnen", "ref": "Frage 16",
     "expect": "Bleib-weg", "key": "inland-stay-away", "why": "deictic"},
    {"bank": "de", "catalogue": "SBF Binnen", "ref": "Frage 162",
     "expect": "Wenden über Steuerbord", "key": "inland-turn-to-starboard",
     "why": "deictic"},
    {"bank": "de", "catalogue": "SBF Binnen", "ref": "Frage 163",
     "expect": "Wenden über Backbord", "key": "inland-turn-to-port",
     "why": "deictic"},
    {"bank": "de", "catalogue": "SBF Binnen", "ref": "Frage 164",
     "expect": "Überholen an der Steuerbordseite",
     "key": "inland-overtake-to-starboard", "why": "deictic"},
    {"bank": "de", "catalogue": "SBF Binnen", "ref": "Frage 165",
     "expect": "Überholen an der Backbordseite", "key": "inland-overtake-to-port",
     "why": "deictic"},
    {"bank": "de", "catalogue": "SBF Binnen", "ref": "Frage 166",
     "expect": "Kursänderung nach Steuerbord",
     "key": "inland-harbour-turn-starboard", "why": "deictic"},
    {"bank": "de", "catalogue": "SBF Binnen", "ref": "Frage 167",
     "expect": "Kursänderung nach Backbord", "key": "inland-harbour-turn-port",
     "why": "deictic"},
    {"bank": "de", "catalogue": "SBF See", "ref": "Frage 141",
     "expect": "Ankerlieger macht", "key": "sea-anchored-warning",
     "why": "deictic"},
    {"bank": "de", "catalogue": "SBF See", "ref": "Frage 162",
     "expect": "Gefahr- und Warnsignal", "key": "sea-general-danger",
     "why": "deictic"},
    {"bank": "de", "catalogue": "SBF See", "ref": "Frage 178",
     "expect": "nicht geöffnet werden", "key": "sea-bridge-lock-closed",
     "why": "deictic"},
    {"bank": "de", "catalogue": "SBF See", "ref": "Frage 186",
     "expect": "Polizeifahrzeug fordert", "key": "sea-official-vessel-stop",
     "why": "deictic"},
    {"bank": "de", "catalogue": "SBF See", "ref": "Frage 188",
     "expect": "Sperrung der Seeschifffahrtsstraße", "key": "sea-waterway-closed",
     "why": "deictic"},
    {"bank": "de", "catalogue": "SBF See", "ref": "Frage 282",
     "expect": "Seenotsignal", "key": "sea-sos", "why": "deictic"},
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
