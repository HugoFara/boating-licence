"""Principle tagging — the join key between a question and its "why" concept.

Roadmap group A/D1: a *principle* is the generative rule a question tests (IALA
buoyage logic, the navigation-light grammar, the give-way hierarchy). One concept
card explains a principle; every question carrying that ``principle`` tag links to
it. Tags are derived **deterministically** here at build time, so re-running the
build yields identical tags (no model, no randomness).

Scope (decided from the data): the pilot tags the two buckets that dominate the
corpus and are genuinely *reconstructable* — signals (~416 q) and give-way rules
(~251 q). Everything else stays untagged ("") and the player simply shows no card,
so the feature degrades gracefully and never mislabels.

The classifier is conservative: it matches language-specific keywords against the
stem + choice text + explanation and assigns the first principle whose keyword
set hits. A small set of *unambiguous* themes (e.g. balisage → iala-buoyage) act
as a fallback when no keyword matched. When nothing is confident, it returns "".

Matching is on **word boundaries**, not raw substrings: plain substring matching
tagged every English question containing "aboard"/"board" as buoyage (the Italian
key "boa"), and every Italian "conoscere" as a day shape ("cono"). A keyword may
opt back into prefix matching with a trailing ``*`` — German compounds inflect
("Topplicht" → "Topplichter") and would otherwise be missed. Precision by
default, recall where the language needs it.
"""

from __future__ import annotations

import re
import sqlite3
import unicodedata

# --- the principle taxonomy (stable, language-neutral slugs) -------------------
# Each entry: slug -> human gloss. The slug is what lands in Question.principle
# and keys the concept bank; the gloss is documentation only.
PRINCIPLES: dict[str, str] = {
    # signals family
    "iala-buoyage":   "Lateral & cardinal marks: the IALA buoyage system",
    "nav-lights":     "Navigation lights: who shows what, and why",
    "day-shapes":     "Day shapes (ball / cone / cylinder)",
    "sound-signals":  "Sound-signal grammar (short / long blasts)",
    "waterway-signs": "Inland-waterway signboards (CEVNI / RGP / SchifffahrtsZ.)",
    # give-way family
    "give-way":       "The give-way hierarchy and steering & sailing rules",
}

# Keyword tables, checked in this priority order. Buoyage runs FIRST inside the
# signals family: a mark is identified by its topmark (a cone, a cylinder) and its
# light rhythm, so "cone"/"feu blanc" used to steal every cardinal-mark question
# for day-shapes or nav-lights. A question about a *mark* is a buoyage question;
# only a vessel's own shape or lights should reach the two tables below.
# A trailing "*" means prefix match (German compounds inflect); everything else
# must match as a whole word. Keep keywords discriminating — a false hit now
# renders a confident concept card next to an unrelated question.
_KEYWORDS: list[tuple[str, tuple[str, ...]]] = [
    ("iala-buoyage", (
        "bouee*", "balise*", "laterale*", "cardinale*", "espar*", "voyant*",
        "eaux saines", "danger isole", "marque speciale", "marques speciales",
        "buoy", "buoys", "buoyage", "lateral mark*", "cardinal mark*",
        "safe water", "isolated danger",
        "special mark*", "port-hand", "starboard-hand", "preferred channel",
        "spierentonne*", "seitenzeichen*", "kardinalzeichen*",
        # NB: bare babord/tribord/backbord/steuerbord/"tonne" are intentionally
        # NOT keywords — port/starboard appear in give-way & steering questions too,
        # so they over-matched. Buoyage is caught by the mark-specific terms above.
        # "boa" is whole-word only: as a substring it hit every English "board",
        # "aboard" and "starboard" in the corpus.
        "boa", "boe", "gavitello*", "acque sicure",
    )),
    ("sound-signals", (
        "signal sonore", "signaux sonores", "son bref", "sons bref*",
        "son prolonge", "sons prolonge*", "sifflet*",
        "sound signal*", "short blast*", "long blast*", "prolonged blast*",
        "whistle*",
        "schallsignal*", "kurzer ton", "langer ton", "pfeife*", "glocke*",
        # declined German forms the nominative keys miss: "Dauer eines kurzen Tons",
        # "vier kurze/kurzen Töne(n)" — the catalogue asks blast questions in the
        # genitive/plural, where "kurzer ton" never matches.
        "kurzen ton*", "langen ton*", "kurze tone", "lange tone",
        "segnale sonoro", "segnali sonori", "suono breve", "suoni brevi",
        "suono prolungato", "fischio*",
    )),
    ("day-shapes", (
        "marque de jour", "marques de jour", "ballon*", "cone", "cones",
        "cylindre*", "boule noire", "boules noires",
        "day shape*", "day-shape*", "black ball*", "black cone*", "cylinder*",
        "signalkorper*", "schwarzer ball", "kegel*", "zylinder*", "rhombus*",
        "segnale diurno", "segnali diurni", "cono", "coni", "pallone*",
        "cilindro*",
    )),
    ("nav-lights", (
        # NB: bare "feu de"/"feux de" are NOT keywords — they also matched "feu de
        # detresse" (a pyrotechnic signal) and "feu de position" on non-light
        # questions. The part-specific forms below carry the recall.
        "feu de mat", "feux de mat", "feu de tete de mat", "feu de cote",
        "feux de cote", "feu de poupe", "feu de mouillage", "feu bicolore",
        "feu blanc", "feu rouge", "feu vert", "feux blancs", "tricolore*",
        "feu visible sur", "feux visibles", "signalisation lumineuse",
        "navigation light*", "masthead light*", "sidelight*", "sternlight*",
        "all-round light*", "all round light*", "stern light*", "anchor light*",
        "topplicht*", "seitenlicht*", "hecklicht*", "rundumlicht*",
        "lichterfuhrung*",
        # generic German light-configuration phrasing the part-specific keys miss:
        # "Was bedeuten diese Lichter", "Welches Fahrzeug führt diese Lichter",
        # "zwei blaue Lichter übereinander". Discriminating — these are light-signal
        # questions, not sound/shape/buoyage (all of which run before this table).
        "diese lichter", "blaue lichter", "lichter ubereinander",
        "lichter fuhren", "lichter gefuhrt", "lichter zeigen", "lichter gezeigt",
        "light signal*", "lichtsignal*",
        "fanale*", "fanali", "luce di", "luci di", "luce bianca",
        "segnalazione luminosa",
    )),
    ("waterway-signs", (
        "panneau*", "signalisation fluviale", "tableau d'eau", "ecriteau*",
        "signal de la voie", "panneau d'interdiction", "panneau d'obligation",
        "signboard*", "waterway sign*", "shore mark*", "notice mark*",
        "tafelzeichen*", "verbotszeichen*", "gebotszeichen*", "hinweiszeichen*",
        "schifffahrtszeichen*",
        "segnaletica", "pannello*", "cartello*",
    )),
    ("give-way", (
        # NB: bare "priorite" is NOT a keyword — radio traffic has degrees of
        # priority too ("MAYDAY correspond à quel degré de priorité"), and it
        # dragged the distress-call questions into the give-way card. Likewise
        # bare "croisement", which matched the crossing of strands in a knot.
        "priorite de passage", "droit de priorite", "bateau prioritaire",
        "bateaux prioritaires", "navire prioritaire", "route libre",
        "privilegie*", "donner la route", "s'ecarter", "doit s'ecarter",
        "route de collision", "routes qui se croisent", "routes se croisent",
        "depassement*", "depasse", "face a face",
        "navire qui doit manoeuvrer", "give way", "give-way", "stand-on",
        "stand on", "overtaking", "overtake*", "crossing situation", "head-on",
        "right of way", "keep out of the way", "keep clear",
        "vorfahrt*", "ausweich*", "kurshalter*", "kurs und geschwindigkeit",
        # "kreuzen" alone means *tacking* in sailing German, so it tagged
        # spinnaker-handling questions; only the course-crossing forms count.
        "kreuzende kurse", "kreuzenden kurs*", "uberholen*", "uberholt",
        "entgegenkommend*", "vorfahrtsregel*",
        "precedenza", "dare la rotta", "sorpasso", "sorpassa*", "incrocio",
        "rotta di collisione",
    )),
]

# Fallback: a theme that is itself unambiguous about its principle. Only used
# when no keyword matched, so it never overrides a confident keyword hit.
_THEME_DEFAULT: dict[str, str] = {
    "balisage":              "iala-buoyage",
    "feux_signaux":          "nav-lights",
    "signalisation_fluviale": "waterway-signs",
    "lights_shapes":         "nav-lights",
    "sound_light_signals":   "sound-signals",
    "steering_sailing":      "give-way",
    "regles_route":          "give-way",
}


def _norm(s: str) -> str:
    """Lower-case, strip accents — so 'priorité' and 'priorite' match alike."""
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower()


def _pattern(kw: str) -> re.Pattern:
    """Compile one keyword. Both ends are word-anchored so a key can't fire from
    inside a longer word; a trailing ``*`` drops the right anchor, which is how
    an inflecting stem ("topplicht*" → Topplichter) opts into prefix matching."""
    if kw.endswith("*"):
        return re.compile(r"(?<!\w)" + re.escape(kw[:-1]))
    return re.compile(r"(?<!\w)" + re.escape(kw) + r"(?!\w)")


# A figure question's stem names the object it is asking about ("Que signifie ce
# panneau ?", "What does this board mean?"); its options are bare captions ("No
# overtaking", "Mandatory to sound the whistle") that belong to whatever the
# pictogram forbids, not to the sign family being examined. Only these
# carrier-naming phrases are consulted stem-first — deliberately NOT the whole
# keyword table, which would let "two black cones" in a cardinal-mark stem beat
# the "cardinal mark" in its own explanation.
_STEM_FAMILY: list[tuple[str, tuple[str, ...]]] = [
    ("waterway-signs", ("ce panneau", "panneau de type", "this board",
                        "board of type", "dieses tafelzeichen")),
    ("nav-lights", ("signalisation lumineuse", "signal lumineux",
                    "this light signal", "segnalazione luminosa")),
    ("sound-signals", ("ce signal sonore", "this sound signal",
                       "questo segnale sonoro")),
]

# Compiled once at import: slug -> [(keyword, pattern)], same priority order.
_COMPILED: list[tuple[str, tuple[tuple[str, re.Pattern], ...]]] = [
    (slug, tuple((kw, _pattern(kw)) for kw in kws)) for slug, kws in _KEYWORDS
]
_COMPILED_STEM: list[tuple[str, tuple[re.Pattern, ...]]] = [
    (slug, tuple(_pattern(kw) for kw in kws)) for slug, kws in _STEM_FAMILY
]

# Themes outside the tagged scope. Knots and safety-equipment questions share
# vocabulary with the signal families (a lifebuoy is a "bouée", a knot crosses
# strands) without ever testing a signal or a steering rule, so no concept card
# can be right for them. Excluding the theme is more honest than chasing each
# collision with a narrower keyword.
_EXCLUDED_THEMES: frozenset[str] = frozenset({"matelotage", "securite"})


def tag_for(stem: str, choices_text: str = "", explanation: str = "",
            theme: str = "") -> str:
    """Return the principle slug for one question's text, or "" if not confident.

    A stem that names the object it asks about ("ce panneau", "this board") wins
    outright: those are figure questions whose options are bare captions that
    otherwise drag a signboard question into give-way or sound-signals. Failing
    that, the full text is matched in priority order, then an unambiguous theme
    is the fallback. Themes outside the tagged scope never get a tag, whatever
    the wording.
    """
    if theme in _EXCLUDED_THEMES:
        return ""
    stem_hay = _norm(stem)
    for slug, pats in _COMPILED_STEM:
        if any(p.search(stem_hay) for p in pats):
            return slug
    hay = _norm(" ".join([stem, choices_text, explanation]))
    for slug, pats in _COMPILED:
        if any(p.search(hay) for _, p in pats):
            return slug
    return _THEME_DEFAULT.get(theme, "")


def tags_present(stem: str, choices_text: str = "", explanation: str = "") -> list[str]:
    """Every principle family whose keywords fire for one question, in priority
    order — NOT just the first (which is what :func:`tag_for` assigns).

    This is the audit lens behind the floor guarantee: when more than one family
    fires (e.g. a give-way question whose vessel is identified by a day-shape), the
    single ``tag_for`` tag is the *highest-priority* family, which may not be the
    *dominant examined* concept. Comparing the two exposes where single-tagging
    pushes a topic's measured weight onto a neighbour — always understating the
    displaced topic, never inflating it (so coverage stays a floor)."""
    hay = _norm(" ".join([stem, choices_text, explanation]))
    return [slug for slug, pats in _COMPILED if any(p.search(hay) for _, p in pats)]


def tag_questions(conn: sqlite3.Connection, overwrite: bool = False) -> dict:
    """Tag every question in a bank in place, writing Question.principle.

    Idempotent and deterministic. By default it only fills *empty* principles
    (so a hand-curated tag is never clobbered); ``overwrite=True`` retags all.
    Returns a stats dict: total, tagged, and a per-principle breakdown.
    """
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, stem, explanation, theme, principle FROM questions"
    ).fetchall()
    by_principle: dict[str, int] = {}
    tagged = 0
    cur = conn.cursor()
    for r in rows:
        if r["principle"] and not overwrite:
            by_principle[r["principle"]] = by_principle.get(r["principle"], 0) + 1
            continue
        ctext = " ".join(
            c[0] or "" for c in conn.execute(
                "SELECT text FROM choices WHERE question_id=?", (r["id"],))
        )
        slug = tag_for(r["stem"], ctext, r["explanation"] or "", r["theme"])
        if slug:
            cur.execute("UPDATE questions SET principle=? WHERE id=?", (slug, r["id"]))
            tagged += 1
            by_principle[slug] = by_principle.get(slug, 0) + 1
        elif overwrite and r["principle"]:
            # The fresh tagger no longer matches, but a tag is on file: clear it.
            # Without this an overwrite can change A→B but never A→"", so a tag would
            # outlive the keyword that produced it (the stale-tag rot that skews the
            # coverage instrument). Re-tagging must be able to RETRACT, not only revise.
            cur.execute("UPDATE questions SET principle='' WHERE id=?", (r["id"],))
    conn.commit()
    conn.row_factory = None
    return {"total": len(rows), "tagged": tagged,
            "by_principle": dict(sorted(by_principle.items()))}
