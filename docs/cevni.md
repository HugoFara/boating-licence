# CEVNI core — the cross-country reusable question pool

National inland-navigation rules are national implementations of **CEVNI** (the
UNECE *Code Européen des Voies de Navigation Intérieure*). The signs, buoyage,
lights and sound signals it harmonises are identical across signatory states — a
lateral mark or a "no entry" board is the same in CH, DE, FR or NL — so a question
that tests them is reusable everywhere; only its legal *citation* re-grounds per
country. That shared core is the bulk of every bank, and exposing it as its own
pool is what makes the multi-country tool more than N separate apps.

This is the **CEVNI** layer. It sits alongside, not inside, the country registry
(`src/countries/`, which owns *what a country is*): CEVNI is a property of
**questions**, derived at build time, country-agnostic.

## The scope taxonomy

`src/cevni.py` assigns every `Question` exactly one scope:

| scope | meaning | examples |
|---|---|---|
| `cevni` | harmonised CEVNI content — portable across signatory states | signs/buoyage/lights/sound signals, navigation (right-of-way) rules, generic seamanship & meteorology, term definitions |
| `national` | country statute — belongs to one country | permit/registration/insurance law, bilateral frontier-water rules |
| `local` | tied to one water body | named local winds (the Léman *bise*/*joran*…), a lake's storm-signal operation |

The `cevni`-scoped questions are the shared core. The classification is a
deliberately **auditable heuristic** (theme-keyed, refined by regexes on
ref/source/stem — read `classify()`), and a *starting point*: tune the keyword
sets for your own law.

## How it ships (and the byte-stability rule)

Scope is **derived, never stored** — it is computed at export time, so the
`Question` schema and the per-language national bundles
(`web/questions.{fr,de,it,en}.json`) are **untouched and byte-identical**. The
core is shipped as **additive** sibling files:

* `run.py` `cmd_web` builds `web/questions.cevni.<lang>.json` (the `cevni` subset,
  same shape as a national bundle, `meta.pool = "cevni"`) and advertises them in
  `web/languages.json` under a `cevni` block (`{lang: {path, count}}`).
* The player (`web/app.js`) offers a **National ⟷ CEVNI core** pool toggle that
  simply re-loads the other bundle. The toggle hides itself when no core bundle
  exists, so a country that hasn't been classified yet loses nothing.

> Invariant to preserve: after `python run.py web`, `git diff` must show **zero**
> change to the four national `questions.<lang>.json`. Only `languages.json`
> (additive keys) and the `questions.cevni.*.json` files may move.

## Adding a country to the core

A country joins the CEVNI core for free as soon as its questions are in the bank:
`cmd_web` classifies every exportable question regardless of country/language. To
make the split accurate for a new country:

1. Confirm the country's national law **implements CEVNI** (most EU inland regimes
   do). Record that on its `Country` in `src/countries/<code>.py` if a field
   exists for it.
2. Skim `src/cevni.py` and extend the keyword sets so *its* statute lands in
   `national` and *its* local waters in `local`. The defaults are tuned for
   Switzerland (Léman winds, Franco-Swiss frontier, VKS permit admin); a German or
   French bank will need its own admin/frontier/local vocabulary or those
   questions will default to `cevni`.
3. Run `python run.py web` and check the build summary's `CEVNI core pool:`
   line + `cevni.scope_counts()` look right (national statute should not leak into
   the core).

## Not CEVNI: Lake Constance (Bodensee)

Lake Constance is **explicitly outside CEVNI** — it has its own tri-national
*Bodensee-Schifffahrts-Ordnung* (BSO) and the *Bodenseeschifferpatent*. Its signs
are therefore **not** portable and must not be classified `cevni`. The Bodensee
permits are owned by the German country module (`src/countries/de.py`, the
`Bodensee-*` permits).

This is **wired**, not just documented: `BODENSEE` is a `shared_water`
jurisdiction with `cevni_relation = "excluded"` in `src/jurisdictions.py`, and
`classify()` calls `jurisdictions.excluded_regime()` first — so any BSO-sourced
question is scoped `local` and can never enter the European core, whatever its
theme. To add another non-CEVNI regime later, declare it in
`src/jurisdictions.py` (`_EXCLUDED_MARKERS`); no change to `cevni.py` is needed.

The jurisdiction layer (`src/jurisdictions.py`) is the descriptive regime view
*over* `src/countries`: it derives each country's display data from the country
registry (no duplication) and adds what a `Country` can't model — the CEVNI
relation itself, plus supra-national (CEVNI) and shared-water (Bodensee) regimes.

## Files

* `src/cevni.py` — `classify`, `core_bank`, `scope_counts`, `SCOPES`.
* `tests/test_cevni.py` — scope-taxonomy contract.
* `run.py` `cmd_web` — the additive CEVNI bundle export + manifest block.
* `web/app.js` — `poolAvailable`/`restorePool`/`selectPool`/`renderPools` + the
  pool-aware `fetchBank`.
