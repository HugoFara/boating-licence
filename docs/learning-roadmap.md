# Learning roadmap — from recognition to understanding

The app can already make someone *pass* the exam (multiple-choice recognition).
This roadmap is about making them *understand* — so a value like "750 N of buoyancy
per person" stops being an arbitrary number to memorise and becomes something the
learner can reconstruct and apply.

## The design principle that unlocks everything

The earlier framing treated "offline player vs. runtime model" as the fork that
gates the deep features. It isn't, because the pipeline **already calls an LLM at
build time** (`src/questions/prose.py` drafts questions behind the review gate). So
the architecture is:

> **Author rich content at build time (LLM + human review gate) → ship it static →
> the player stays 100 % offline and dependency-free.**

Every feature below keeps that property. No feature requires a runtime API key.

## Exam fidelity is preserved

The real exam is multiple-choice, so we must keep training recognition. Therefore
**all of this lands in practice mode**; exam mode keeps mirroring the real format
byte-for-byte. The split already exists in the player (`state.mode === "practice"`).

## The four groups

### Group A — The "why" layer  *(the core motivation)*

The existing `explanation` field is one sentence that *cites* the rule. It says
*what*, never *why*. Group A adds a separate, reusable **concept** content type — a
small set of generative explainers, each linked to the questions it underlies.

- **A1 — Physical / natural rationale.** Why fog forms, why a gust front arrives
  before the rain, why a displacement hull has a hull-speed limit, why 750 N keeps
  an unconscious adult's airway above water. Meteorology / physics, not law.
- **A2 — Legal-value rationale.** Why the law *picked* a number.
  **Policy (decided): sourced-only, never invented.** Where no source states the
  legislator's intent, explain *what the value guarantees* (derivable from physics
  or a cited standard) rather than guessing the intent. Same hard rule as questions:
  the source is the authority — see `memory/source-questions-never-recall.md`.

Mechanism: a `concept` record (id, title, body, source/provenance, linked question
ids + principle tag), surfaced in the player as a "Learn" card before/after the
questions that test it. New content type; highest effort; pure build-time + review.

### Group B — Turn existing MCQs into retrieval  *(player-side, cheap)*

- **B1 — Recall-first reveal.** In practice, show the stem first and make the
  learner commit (optionally jotting a free-text answer) *before* the options
  appear. Converts every existing question from recognition to recall. No data
  change.
- **B2 — Diagnostic distractor feedback.** On a wrong pick, name the specific
  confusion instead of just "the answer is B". *Nearly free for figure questions* —
  each distractor is itself another figure's caption, so we know what the wrong
  choice means and where it really comes from. For prose questions it uses a new
  per-choice `rationale` field, authored at build time (empty for now → graceful
  fallback to the chosen-vs-correct contrast).
- **B3 — Self-explanation (offline form).** Prompt "why?" → learner articulates →
  reveal the rule → self-score. The generation benefit survives without a grader.
  *(Deferred behind B1/B2.)*

### Group C — Durability  *(player-side, localStorage)*

- **C1 — Spaced repetition + interleaving.** Per-question history in `localStorage`
  (a Leitner box + last-seen timestamp). A "spaced review" practice ordering draws
  *due* and *weak* and *never-seen* items first, interleaved across themes
  (interleaving improves the signal discrimination this domain lives on).
- **C2 — Confidence capture + hypercorrection.** Ask confidence with each practice
  answer; prioritise **high-confidence-wrong** items for resurfacing and flag them
  in the review. Those are the dangerous-on-the-water errors, and once corrected
  they stick unusually well.

### Group D — Transfer  *(build-time LLM, highest payoff)*

- **D1 — Principle clustering.** Tag each question with the generative principle it
  tests (IALA buoyage logic, the short/long-blast grammar, the give-way hierarchy).
- **D2 — Scenario pools.** Build-time-generated *novel* scenarios grounded in the
  cited rule, review-gated, shipped static. Distractors become plausible
  *misapplications* of the rule. *(Builds on A's principle tags.)*

## Cost map (grounded in the actual code)

| Item | Data-model change | Player change | Offline | Effort |
|------|-------------------|---------------|:------:|:-----:|
| B1 recall-first | none | reveal flow | ✅ | XS |
| B2 figures | none (derive) | reveal | ✅ | S |
| B2 prose | `+ Choice.rationale` (additive) | reveal | ✅ | M (authoring) |
| C1 spacing | none (localStorage) | scheduler module | ✅ | M |
| C2 confidence | none (localStorage) | reveal UI + scheduler | ✅ | S |
| A why-layer | new `concept` type + link | "Learn" card | ✅ | L (content) |
| D transfer | `+ principle` tag + generator | scenario render | ✅ | L |

The schema is friendly to this: `src/questions/schema.py` already does additive
idempotent migrations (`_migrate`) and exports via `asdict`, so a new field flows
through to the player automatically.

## Sequence (decided)

1. **Phase 1 + 2 (this pass) — all player-side, offline, no content backlog:**
   B1 recall-first · B2 diagnostic feedback (figures now, `Choice.rationale` field
   wired for prose later) · C1 spaced + interleaved · C2 confidence + hypercorrection.
   Practice-mode settings persist in `localStorage`; exam mode untouched.
2. **Group A — the "why" content layer.** Design the `concept` type; pilot the
   highest-leverage themes end-to-end, then scale authoring through the review gate.
3. **Group D — transfer.** Principle tags → scenario pools.

### Group A pilot — retargeted by the data (2026-05-31)

The original A1/A2 pilots (meteorology; buoyancy / 750 N) were *hand-picked*. A
count of the actual banks overturned them — they're the tail, not the head:

| Reconstructable bucket | Questions (all banks, grounded langs) |
|------------------------|--------------------------------------:|
| **Signals** (marks, lights, day-shapes, sounds, waterway signs) | **~416** |
| **Give-way** (steering & sailing rules)                          | **~251** |
| meteorology *(was the A1 pilot)*                                 | ~49 |
| safety *(holds the 750 N value)*                                 | 17 |

Signals and give-way both dominate the corpus **and** are the most genuinely
generative (a small rule-set reconstructs hundreds of answers). So the pilot is
**signaux + priorité**, with 750 N kept as one A2 specimen inside the safety set.

**Structural foundation built (this pass):**
- `Concept` content type + additive `Question.principle` join key
  (`src/questions/schema.py`), with idempotent migration + review-gated export.
- Deterministic principle tagger (`src/questions/principles.py`): 6 principle
  slugs across the two families; `python run.py concepts` tags every bank
  (~870 questions tagged) and the web bundlers run it so the tag ships in the
  question JSON.
- Player **"Learn" card** (`web/app.js conceptHtml`): a collapsible per-principle
  explainer shown at reveal/review, loaded from `concepts.<lang>.json`. Absent
  bank → no card (graceful, still 100% offline).
- Tests: `tests/test_concepts.py` (schema round-trip, review gate, tagger).

**Remaining for Group A:** author the sourced concept bodies (sourced-only, never
invented) behind the review gate — the cards light up the moment content exists.

## Settings the player gains (practice only)

A JS-built practice-settings panel (no per-country HTML change needed), each toggle
persisted in `localStorage`:

- **Recall-first** (B1)
- **Confidence rating** (C2)
- **Spaced review** ordering (C1)

## Group E — the illustration system  *(started 2026-08-15)*

This domain is visual and the corpus is not. Counted across every bank:

| principle | questions | with a figure | missing |
|---|---:|---:|---:|
| nav-lights | 196 | 18 | **178** |
| waterway-signs | 187 | 127 | 60 |
| give-way | 148 | 11 | **137** |
| sound-signals | 87 | 11 | 76 |
| day-shapes | 70 | 3 | **67** |
| iala-buoyage | 49 | 7 | 42 |

**560 of 737** principle-tagged questions ship without a picture; both French banks
(292 questions) and the INT bank (57) have **none at all**. Worse, 27 German
questions are *unanswerable as shipped* — their stem points at a figure ("Welches
Fahrzeug führt **diese** Signalkörper?") that was never ingested.

Obtaining the missing images does not work, and that is the structural point: the 95
we have are scraped rasters from two sources with **incompatible reuse terms** —
ONI/RNL via Fedlex (public domain) and ELWIS GIFs (§5(2) UrhG, verbatim only). A
diagram acquired for one country's bank may not be reused in another's, which is
exactly what the harmonised core in [`scope.md`](scope.md) is supposed to enable.

### The way out: derive, don't obtain

Four of the six families are **geometry, not artwork** — the law describes them:

* **day shapes** — balls, cones, cylinders, diamonds, hourglasses in a vertical line
* **nav-lights** — arcs at 112°30′ / 135° / 225°, by colour and height
* **sound-signals** — a timeline of short and long blasts
* **iala-buoyage** — shape + colour bands + topmark + rhythm

So the figure is *generated from the article that prescribes it*, under the project's
own licence — which makes one drawing valid in **every** bank and language. Only
`waterway-signs` is genuine pictogram artwork, and it is the family already best
covered (127/187).

### The discipline (same as questions)

`src/questions/diagrams.py` holds the spec. Every diagram carries the exact `quote`
from the article prescribing its shapes, and `tests/test_diagrams.py` reads that
fragment back out of the KB — **a drawing that drifts from the law fails the build**,
because a wrong diagram teaches a wrong shape and is worse than no diagram. Nothing
is drawn from memory (same rule as `memory/source-questions-never-recall`).

Attachment is deliberately narrow. A diagram is attached only where the figure is the
**subject** of the question, on one of two recorded grounds:

* `deictic` — the stem points at a figure that was never shipped (these are the
  broken questions; the figure *is* the question);
* `named-in-stem` — the stem already names the shape in words, so the picture
  restates it and can give nothing away.

It is **never** attached where the shape is the *answer* ("what signal does a vessel
unable to manoeuvre show?") — that would turn a question into a giveaway. Those are
served by the concept card at reveal time instead. Two interlocks re-check the claim
at build time: the correct answer must still contain the expected wording, and a
`deictic` stem must still be deictic. When either trips, the assignment **refuses**
rather than illustrating the wrong thing.

Attaching a figure never touches question text, which is what keeps the German bank
compliant: the ELWIS catalogue is reusable only *unverändert*, so the diagram is
added *alongside* the verbatim question exactly like the concept card and the choice
rationales, and the SVG says in its own source that it is original artwork, not a
reproduction of any official figure.

### Status

**Day shapes, done:** 10 diagrams sourced to SeeStrO 1972 (KVR) Regeln 24–30,
covering the whole shape vocabulary — ball, cone up/down, cylinder, diamond,
hourglass, flag "A" — and the 1–3 shape stacks the rules build from them.

**Nav-lights, done (sea):** 10 diagrams, a vessel seen from ahead at night. The view
is not a styling choice — it is the only aspect that shows both sidelights, and it
forces two facts the drawing must get right:

* **green appears left, red right.** Regel 21 b) puts green to starboard and red to
  port; bows-on, the vessel's starboard side faces the observer's left. Mirroring
  that would teach the exact opposite of the Rule, so `test_diagrams.py` pins it.
* **no sternlight is drawn.** It shines over 135° from right astern (Regel 21 c), so
  from ahead it cannot be seen. Its absence is part of the lesson.

The vertical layout is likewise dictated: Anlage I §2 f) i) puts masthead lights above
all other lights, §2 g) keeps sidelights low, §2 i) iii) spaces a three-light line
evenly, §2 k) puts the forward anchor light higher than the after one. §2 j) is the
binding constraint on the canvas — the lower of a fishing vessel's two all-round
lights must clear the sidelights by at least twice its distance from the upper one —
and that inequality is asserted in the module and in the tests.

The pairs are where the teaching is: Frage 97/98 (not under command) and 102/103
(restricted in her ability to manoeuvre) differ **only** by the sidelights, because
the Rules prescribe the identity lights always and the sidelights only *bei Fahrt
durchs Wasser*. Two pictures say that better than a sentence.

**16 of the 27 broken German questions are now answerable.** They scope to `colregs`,
so the same figures reach the pooled harmonised core and serve English and French
learners too.

**Deliberately not drawn.** Regel 30 d) has a vessel aground show the anchor light(s)
of a) or b) *plus* two red all-round lights "dort, wo sie am besten gesehen werden
können": the order inside each group is fixed, between them it is not. So Frage 105
and 107 stay unillustrated rather than have us invent a stacking order — recorded in
`_UNPRESCRIBED`. Frage 93/94 (towing convoys) need a second vessel and wait for the
give-way view; the six inland questions need BinSchStrO sourcing, not KVR.

**Sound signals, done:** 13 diagrams, a blast timeline — each blast a bar whose
*width* is its duration, separated by the pause the annex prescribes. That is not a
stylisation: BinSchStrO Anlage 6 already draws its signals as ▬ and ▪ glyphs and
states the durations behind them ("kurzer Ton: etwa eine Sekunde; langer Ton: etwa
vier Sekunden; die Pause … etwa eine Sekunde"). Drawing to scale says what the glyphs
cannot — a long blast is **four times** a short one, which is the entire
discrimination in the inland set: 2 long + 1 short (overtake to starboard), 2 long +
2 short (to port), 3 long + 1 short (leaving harbour to starboard), 3 long + 2 short
(to port). Four things to memorise become one pattern to read.

No second scale is printed on the figure: the inland code fixes the long blast at
about four seconds and KVR Regel 32 allows four to six, so a numeric axis would claim
a precision one of the two codes does not have. The ratio is common to both.

Inland and sea signals are kept apart — the same rhythm can mean different things
under the two codes, so a diagram is only attached to a question from the catalogue
whose code it was drawn from.

### The German gap was mostly our bug, not a missing source

Chasing the truncated stem of `Frage 140` turned up the real cause of the German
figure gap, and it was **not** that ELWIS ships no pictures. Two defects in
`src/questions/elwis.py`:

1. **84 official figures were silently discarded.** `_is_figure()` accepted images
   under `/Grafiken/` and `/Anlagen/Anlage-…` only. The figures published *with* a
   catalogue question live under `/Fragenkatalog-…/` (`Lichter-Frage-105-gif.gif`),
   so every one of them failed the filter — including the pictures for exactly the
   questions whose stems say *"diese Lichter"*.
2. **Nine stems shipped truncated.** ELWIS puts some figures *inside* the question
   paragraph, which is invalid nesting (`<p>` within `<p>`). The parser closes the
   stem at the picture and the rest of the sentence survives only as that element's
   tail, so `Frage 140` ended mid-bracket at *"(mindestens"* and four questions lost
   their "?". The tail is now sewn back on, and a bracket pair left empty by moving
   the figure to its own slot is closed up — the only character-level edit, and the
   original never showed a learner "()".

Fixed by widening the allow-list and by backfilling figures the *cached* pages
already reference, so the catalogue pages are not re-fetched and the questions stay
byte-stable (only the 9 repaired stems change id). The German bank goes from **91 to
145 figures**.

**So the generated diagrams were, for German, largely working around this bug.** Of
the 29 they filled, ELWIS turns out to publish the official figure for 28; the
precedence rule — an official source figure always beats a generated one — retired
them automatically the moment the parser was fixed, which is the design working as
intended. One is still ours (`Frage 96`), and one question still has no figure at
all (`Frage 195`, SBF Binnen).

**Where the generated set still earns its keep is unchanged and untouched:** the two
French banks (292 questions) and INT (57) have **zero** images, and their sources
publish none. ELWIS figures cannot fill that gap — §5(2) permits reuse *unverändert*
and they are German-catalogue artefacts, so they are not portable to another
country's bank, which is precisely the constraint the generated set exists to beat.
Those 33 diagrams are drawn, sourced and tested; what remains is to attach them to
the FR/INT/CH questions. That is now the next step, ahead of drawing more.

### FR / INT / CH: the figures belong on the card, not the stem

Attaching the diagrams outside Germany turned up a hard fact. Counted across the
three families drawn so far, the French and INT banks contain **zero** questions
phrased at a figure — no "ce panneau", no "these lights". Every one is answer-side:
*"De nuit, un navire de moins de 50 m au mouillage montre :"*. Illustrating those
stems is precisely what the attachment rule forbids, because the picture would be
the answer.

So they are served where that was always going to work: the **concept card**, which
opens at reveal. `Concept.figures` (additive) carries the principle's vocabulary
strip, and the card can safely show what an answer looks like — "what shape does a
vessel aground show?" cannot carry its own answer, but the card the learner reads
afterwards can.

**One picture, one citation per code.** A drawing is geometry and travels; a citation
does not. Telling a French learner his day shape comes from *SeeStrO 1972 Regel 27*
would be asserting German law at him, and the codes do genuinely diverge — Swiss
inland balls are painted green, white or yellow where COLREG's are black. So every
diagram carries a citation **per regime**, each verified against that regime's own
KB, and a diagram is offered to a bank only if that bank's law can account for it:

| bank | code cited | diagrams |
|---|---|---:|
| `de` | KVR · SeeSchStrO · BinSchStrO | 33 |
| `int` | COLREG 1972 | 18 |
| `fr_cotiere` | COLREG (as enacted: RIPAM) | 18 |
| `fr_eaux_interieures` | RGP (Code des transports A4241-*) | 6 |
| `ch` | ONI · RNL | 5 |

The strips are **derived, not hand-listed** — every diagram of the card's family the
bank can cite, in spec order — so adding a diagram lights it up on each card entitled
to it and no list can fall out of date.

Two bugs the tests caught while wiring this, both worth keeping the checks for:
a COLREG citation that never mentioned a light (the exemption clause, picked for the
"under 50 m" wording), and an ONI diving-board citation that landed on a *nav-light*
entry — real quote, wrong drawing, waved through by the does-this-text-exist check.
There is now a second test requiring a citation to **name what is drawn**.

### Give-way: plan views, and the one family that must stay off the stem

Six diagrams, and the family where a picture does the most work: the rules read as
word puzzles — *"the vessel which has the other on her own starboard side"* — and
resolve instantly as geometry. Two conventions carry each drawing, neither needing a
caption, which matters when one figure serves four languages:

* the **give-way** vessel is solid, with a **curving** arrow — she is the one that alters;
* the **stand-on** vessel is open, with a **straight** arrow — she holds course and speed.

Nothing is colour-coded red/green on purpose: those two colours already mean port and
starboard throughout the nav-light figures, and reusing them for roles would collide
with the convention the learner is being taught.

`overtaking-stern-sector` shades the 135° arc astern, because Rule 13(b) defines
overtaking as coming up from more than 22.5° abaft the beam — *"at night she would be
able to see only the sternlight … but neither of her sidelights"*. That is the same
arc as the sternlight in the nav-light figures, so the two families explain each
other. `inland-upstream-yields` draws banks and a flow arrow: without the current on
the page there is nothing to tell a *montant* from an *avalant*, and the whole inland
meeting rule is about which is which.

**These are card-only.** Unlike every other family they *show who gives way*, which
is the answer to the questions they illustrate. Safe on a card that opens at reveal,
never on a stem — and a test enforces that no assignment can ever place one.

Reach: `int`/`fr_cotiere` 4 (COLREG 12–15), `fr_eaux_interieures` 3 (RGP A4241-53-5/6),
`de` 1 (BinSchStrO § 6.04), `ch` 1 (ONI art. 63).

### Buoyage: three channels, and the one drawing that must not be wrong

Fourteen marks. A buoy encodes its meaning in three independent channels — body
**shape**, body **colour** (bands, or stripes), and **topmark** — so the renderer
takes exactly those three and can say nothing the source did not.

The cardinal topmark is why this family is worth drawing at all: **the two cones
point at the safe water.** North both up, south both down, east base to base, west
point to point. Read that way the four marks stop being a list and become one rule.

And it is the highest-consequence drawing in the whole set, because a learner who
reads it wrong passes the wrong side of a danger. The first draft had **east and west
transposed**. `test_the_cardinal_cones_point_at_the_safe_water` now reads the cone
apexes straight out of the rendered SVG and pins all four (with a negative control
confirming a swapped mark fails it).

**Two schemes, one shared component.** IALA R1001 region A serves the coastal bank;
the Swiss inland scheme is a genuinely different system — no black-and-yellow
cardinal bodies, marks that may be *"peint en rouge ou non peint"*. What the two
share is precisely the cone pairs, so those diagrams carry a citation in each code
while the bodies beneath them do not. The Swiss marks ride a bare spar rather than an
invented white buoy, because the annex prescribes the shape on top and leaves the
support unpainted — asserting a colour there would be inventing one, and a test
holds that line.

Reach: `fr_cotiere` 9 (IALA R1001 §2.1–2.5), `ch` 5 (ONI Annexe 4 figs 49/50/54).

That completes the five drawable families: **56 diagrams**, every citation verified
against its own code's KB and required to name what is drawn. Card strips now carry
`fr_cotiere` 31 figures, `de` 34, `int` 22, `ch` 11, `fr_eaux_interieures` 9.

### Waterway signs: the family that cannot be derived

This is where deriving runs out, and the reason is worth recording. Every diagram
above exists because the law *describes the figure in words* — "zwei Bälle senkrecht
übereinander", "deux cônes noirs base à base", "ein langer Ton, ein kurzer Ton". The
sign annexes do not do that. ONI Annexe 4, BinSchStrO Anlage 7 and SeeSchStrO Anlage I
each name what a board **means** and show what it **looks like** only in the
accompanying graphic. Checked directly: `bord rouge`, `bordure rouge`, `carré bleu`,
`fond bleu` return **zero** units across the Swiss and German KBs.

Drawing a red-bordered board anyway would be authoring appearance from memory, which
is the one thing this project forbids
(`memory/source-questions-never-recall`). So no sign is derived.

What *can* be done is what fixed the German bank: the picture usually already exists.
Ten of the eleven unillustrated Swiss sign questions had their official ONI/RNL
graphic sitting in the KB's `assets` table, linked by `prov_unit_id` and simply never
wired to the prose questions that name it.

**Seven are shown in the stem** (`named-in-stem` — the stem describes the board and
the answer is its meaning). **Three are unveiled after the answer** (`answer-side`),
because there the board's appearance *is* what is being asked: *"quel pavillon…?"*,
*"quale segnaletica notturna…?"*, *"comment le panneau lettre « A » doit-il être
présenté ?"*. A bulk attach would have spoiled exactly those three.

**The RGP annexes are now ingested — and annexe 5 turns out to be a stub.** The
citation *"RGP, annexe 5, panneau A.1"* was real: LEGI carries the annexes as
articles numbered *"Annexe N à l'article A4241-…"*, which the `^[LRAD]4\d{3}` filter
had been dropping. All nine are in (`code_transports` 1160 → 1169).

But annexe 5 contains **no sign descriptions at all** — 2 179 characters that say
*"Vous pouvez consulter les clichés dans le JO n° 200 du 29/08/2013"* and link a PDF.
Annexe 7 ("caractéristiques techniques") gives sizes, retroreflective film class and
lettering standards; no colour, no shape. Annexe 3 (vessel signals) is the same shape
of stub. **The RGP puts every figure in Journal Officiel plates and LEGI carries only
the surrounding prose**, so French inland sign appearance cannot be text-sourced at
all. The seed questions' visual claims come from those plates; the honest fix is to
ingest the JO PDF and extract them, exactly as the ONI pipeline already does for
Switzerland (`data/assets/oni/image*.png`).

What the annexes *did* unlock is buoyage. **Annexe 8** (18 070 characters,
"Balisage des voies de navigation intérieure") is real text, and its harbour-entrance
and restricted-zone marks are described in words:

* *"A bâbord en entrant : dispositif, en général de forme cylindrique, de couleur rouge"*
* *"A tribord en entrant : dispositif, en général de forme conique, de couleur verte"*
* *"Couleur : jaune … Voyant (le cas échéant) : un seul « X » jaune"*

So three buoyage diagrams gain a French inland citation, and
`fr_eaux_interieures` gets a mark strip it did not have. One candidate was refused:
the groyne mark's *"le caractère d'un cône vert pointe en haut et rouge pointe en
bas"* does not say whether that is one stacked pair or two bank-dependent variants,
so nothing is drawn (recorded in `_UNPRESCRIBED`).

The rebuild also exposed a build-order bug: `kb.fr.sqlite` holds the LEGI law *and*
the hand-curated reference corpus (IALA, SHOM), and `legi build` dumped the whole
database into the committed LEGI corpus — folding 19 reference units into it.
`export_json` now takes a `sources` filter, and the two tests that caught it stay as
the guard.

### Adding a diagram (the smallest useful contribution)

1. Add an entry to `DAY_SHAPES` or `NAV_LIGHTS` in `src/questions/diagrams.py`: the
   stack of shapes (or the column of lights, top to bottom, plus whether the vessel
   is making way), a title that describes **the figure and not its meaning**, and a
   `source` naming the KB unit, the article, and the fragment that prescribes it.
2. Add an `ASSIGNMENTS` entry only if some question's figure is the subject — with
   the `why` and the `expect` interlock.
3. `python run.py diagrams` then `python tests/test_diagrams.py`. The sourcing test
   is the review: if your quote is not in the law, the diagram does not ship.

