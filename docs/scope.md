# Question scope — the regime tree and the harmonised core

Navigation law composes by **lex specialis derogat legi generali**: the more
specific regime overrides the more general one, and what it does *not* override is
inherited from the broader set. So the regimes form one tree, each node a
**precision under a larger set** (its parent), and a question sits at the narrowest
rung that governs it:

```
UNIVERSAL                         seamanship valid on any water, any country
├─ CEVNI                          inland traffic code (signs/lights/sounds/rules)
│  ├─ CH-INLAND  (implements)     ONI/RNL — Switzerland
│  ├─ DE-INLAND  (implements)     BinSchStrO
│  ├─ FR-INLAND  (implements)     RGP — eaux intérieures
│  ├─ RHINE      (diverges)       CCNR / RheinSchPV
│  ├─ LEMAN      (diverges)       Franco-Swiss règlement
│  └─ BODENSEE   (excluded)       BSO — its own code; signage NOT portable
└─ COLREGS                        maritime traffic code (the sea base)
   ├─ DE-MARITIME (implements)    SeeSchStrO / KVR — SBF See, SKS, SSS
   └─ FR-MARITIME (implements)    RIPAM — option côtière
```

Two modules realise this, kept distinct:

* `src/jurisdictions.py` — the **regime tree**. Bases (`UNIVERSAL` → `CEVNI`,
  `COLREGS`), then one node *per country per track* (inland/maritime) **derived**
  from `src/countries`, then the shared/special waters declared by hand. Each node
  records its parent (`refines`) and how it sits under it (`relation`:
  `implements` / `diverges` / `excluded` / `is_base`). The **base ancestor** a node
  reaches (`base_of`) is its portability class.
* `src/scope.py` — the **question classifier**. It places each `Question` at one
  rung, country-agnostic and derived at build time.

## The scope taxonomy

`src/scope.py` assigns every `Question` exactly one scope — three **bases** (the
portable, shareable core) and two **overlays**:

| scope | kind | meaning | examples |
|---|---|---|---|
| `universal` | base | seamanship portable under *any* code | knots, generic weather, engine, first aid, environment |
| `cevni` | base | harmonised **inland** traffic code | inland signs/buoyage/lights/sounds, inland right-of-way |
| `colregs` | base | harmonised **maritime** traffic code | sea buoyage/lights, RIPAM/KVR collision rules |
| `national` | overlay | country statute | permit/registration/insurance law, bilateral frontier waters |
| `local` | overlay | tied to one water body | named local winds (Léman *bise*/*joran*…), an *excluded* regime (Bodensee/BSO) |

The **harmonised core** of a permit is `universal` + its track's base — `cevni` for
an inland permit, `colregs` for a sea permit. National/local are the overlay a
single country adds. The classifier is a deliberately **auditable heuristic**
(theme-keyed, refined by regexes on stem/ref/source — read `classify()`), run
narrowest-first (lex specialis), and a *starting point*: tune the keyword sets for
your own law.

## How it ships (and the byte-stability rule)

Scope is **derived, never stored** — computed at export time, so the `Question`
schema and the per-language national bundles
(`web/questions.{fr,de,it,en}.json`) are **untouched and byte-identical**. The core
ships as **additive** sibling files, one per base.

### The core is *global* — pooled across every bank

`cmd_web` does **not** classify one country's bank in isolation. It pools the
base-scoped questions from **every** question bank on disk
(`data/questions*.sqlite` — CH + DE + the per-option FR banks), so a learner
studies the *merged* harmonised material — the German SBF-See and the French
côtière COLREGS questions in one pool, not one country's slice. Mechanics:

* For each bank, classify its exportable questions, export per language, and collect
  the base-scoped ones; pool per `(base, language)`, **dedupe by id**.
* Write `web/questions.<base>.<lang>.json` (`meta.pool = "<base>"`,
  `meta.grounding` naming the canonical basis) and list them in `languages.json`
  under a `core` block (`{base: {lang: {path, count}}}`).
* **Grounding:** `colregs` is anchored to the canonical **COLREG 1972** text (the
  `INT` layer — a public-domain USCG reproduction); `cevni` to the national inland
  enactments (the UNECE CEVNI text is not redistributable, so there is no canonical
  bundle — see `src/countries/intl.py`).

> **Language-bounded.** The pool is per language: a German See question enters a
> French learner's core only once **translated**. Until then each language's core is
> the union of *that language's* banks (e.g. `colregs` today: `de=179, fr=20,
> en=20`). The merge is what makes translation pay off across countries.

### Track-gated consumption

The player (`web/app.js`) offers a **National ⟷ Common core** toggle, and composes
the core **by the active permit's track** (`activeTrack()`): an inland permit gets
`universal + cevni`, a sea permit `universal + colregs` — never both traffic codes
at once. Each bundle is fetched with its own FR fallback and merged, deduped. The
manifest carries each permit's `track`; the toggle hides itself when no core exists.

> Invariant to preserve: after `python run.py web`, `git diff` must show **zero**
> change to the four national `questions.<lang>.json`. Only `languages.json`
> (additive keys) and the `questions.<base>.*.json` files may move.

## Adding a country to the core

A country joins the core for free as soon as its questions are in the bank:
`cmd_web` classifies every exportable question regardless of country/language. To
make the split accurate for a new country:

1. Confirm which tracks its permits cover. Set `Permit.track` (`inland` /
   `maritime`) on each permit in `src/countries/<code>.py`; when unset, the
   jurisdiction layer infers it from the permit code/label. Each track yields a
   regime node under `CEVNI` (inland) or `COLREGS` (maritime).
2. Give `src/scope.py` a branch for the country's theme namespace if it differs
   from the Swiss one (the disjoint namespaces let each branch run without touching
   the others). Switzerland uses the default theme rules; **France** has
   `_classify_fr` (keyed on `_FR_THEMES`); **Germany** has `_classify_de` (keyed on
   `_DE_THEMES`) which reads the **exam block** — `spezifisch_see` → `colregs`,
   `spezifisch_binnen` → `cevni` — because the German bank mixes both tracks under
   shared themes. Extend the markers (`_MARITIME`, `_NATIONAL_*`, `_LOCAL_*`) for the
   country's sea / statute / local-water vocabulary.
3. Run `python run.py web` and check the build summary's `global harmonised core:`
   line (per-base counts, pooled over N banks) — national statute should not leak
   into a base, and sea content should land in `colregs`, not `universal`.

> The Bodensee/excluded-regime guard runs **before** any country branch, so a
> German-themed BSO question still scopes `local`, never a base.

### Seed-driven countries (France): both global and local

France is **seed-driven** (no Fedlex fetch/parse) and ships its own self-contained
players under `web/fr/<option>/`, each with its own local per-base core emitted by
`src/fr/build_fr.py`. It *also* joins the global pool: its per-option banks
(`data/questions.fr_*.sqlite`) are on disk, so `cmd_web` pools them into the global
core like any other bank. So France's questions live in **both** its boutique
players (local core) and the shared global core; per language the two are equivalent
today (a French côtière question is the same wherever it's served). Folding France's
players onto the global bundles is a later simplification; functionally the merge
already includes France.

## Not CEVNI: Lake Constance (Bodensee), and divergent waters

Lake Constance is **explicitly outside CEVNI** — its tri-national
*Bodensee-Schifffahrts-Ordnung* (BSO) and *Bodenseeschifferpatent* replace the
inland code, so its signage is **not** portable. This is **wired**, not just
documented: `BODENSEE` is a `shared_water` jurisdiction with `relation =
"excluded"`, and `classify()` calls `jurisdictions.excluded_regime()` first — so
any BSO-sourced question is scoped `local` and can never enter a base, whatever its
theme. To add another *excluded* regime later, declare it in `src/jurisdictions.py`
and add its marker to `_EXCLUDED_MARKERS`; no change to `src/scope.py` is needed.

Bodensee is one instance of a **category**. The Rhine (`RHINE`, CCNR/RheinSchPV)
and the Léman (`LEMAN`, Franco-Swiss) also have their own regimes, but they merely
**diverge** from CEVNI (own deviations over a CEVNI base) rather than replace it —
so they keep `relation = "diverges"` and their harmonised signage *stays* in the
core. Only `excluded` regimes are guarded out.

## Files

* `src/jurisdictions.py` — the regime tree (`get`, `codes`, `base_of`, `relation`,
  `track`, `ancestors`, `excluded_regime`, `as_manifest`).
* `src/scope.py` — `classify`, `core_bank`, `ids_by_base`, `bases_present`,
  `scope_counts`, `SCOPES`/`BASES`/`OVERLAYS`.
* `tests/test_jurisdictions.py`, `tests/test_scope.py` — the contracts.
* `run.py` `cmd_web` — the additive per-base core bundles + the `core` manifest.
* `web/app.js` — the pool-composing `fetchBank` + `poolAvailable`/`selectPool`.
