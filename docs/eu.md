# The EU layer — Union acts (`EU`)

A second supra-national member alongside `INT`, and deliberately a different kind
of thing. `INT` holds the **traffic codes** — COLREG, and CEVNI if UNECE ever
clears it — the rules of the road, which the regime tree orders by water. The Union
acts here do not tell you who gives way; they govern **the boat, its certificate
and your qualification**, and they apply Union-wide regardless of which water you
are on.

Like `INT`, this is a **sourcing-only** member: no permits, no exam, no player
bundle. `run.py web` skips it and `src/jurisdictions.py` generates no regime node
for it.

## It adds no base to the regime tree — on purpose

A design category is not a third traffic code. It is portable content that holds
under *any* traffic code, which is exactly what the `universal` base already means
— and what `src/scope.py` already does with the French questions on CE categories.
So EU units ground `universal` and the tree is untouched.

This is pinned by a test (`tests/test_eu.py::test_the_eu_layer_adds_no_regime_node_and_no_new_base`),
because a fourth base would shift every scope decision and the player's
National ⟷ Common-core toggle underneath it.

## The acts

| id | Act | Why it earns its place |
|----|-----|------------------------|
| `rcd` | **Directive 2013/53/EU** on recreational craft and personal watercraft | Directly examinable. Annex I fixes design categories A–D by wind force and significant wave height — the most-asked "European" question in every national bank — plus CE marking, the builder's plate and the craft identification number. |
| `iwt_tech` | **Directive (EU) 2016/1629** on technical requirements for inland waterway vessels | Defines the Union inland navigation certificate and the classification of inland waterways (the zones national permits refer to). |
| `iwt_quals` | **Directive (EU) 2017/2397** on the recognition of professional qualifications in inland navigation | The reason a Dutch, German or French inland certificate is recognised across the Union. The Dutch acts cite it on nearly every page. |

Current size: **159 units** in English (`data/kb.eu.sqlite`).

## The legal boundary

This passes the project's reuse bar more cleanly than any other source it has.
EUR-Lex states that reuse of its legal documents is authorised for **commercial and
non-commercial** purposes under **Commission Decision 2011/833/EU**; the editorial
content and consolidated texts are additionally **CC BY 4.0**, and the metadata is
**CC0**. Attribution is required and is carried per unit.

**Not ingested:** the harmonised **EN ISO standards** the directives point at (the
series behind "presumption of conformity" — stability, buoyancy, freeboard, fuel
systems). Those are CEN/ISO works, sold per copy and all-rights-reserved. The
directives' *reference* to them is ingested; their text never is.

Also documented but not ingested: **UNECE Resolution No. 40** (the ICC). Not EU law,
but the instrument that makes a national pleasure-craft licence travel — the Dutch
klein vaarbewijs is issued on the "klein vaarbewijs/ICC" model, and France issues an
ICC to permit holders. Like CEVNI it is UNECE material and all-rights-reserved.

## One act, 24 languages — and what that costs

An EU act exists in 24 equally authentic language versions. That is the layer's
biggest asset (it feeds the Dutch, German, French and Italian banks from one
source) and it forces two design decisions:

**Refs are language-neutral.** EUR-Lex localises the word "Article", so a ref built
from the page label would read `Artikel 12` in Dutch and `Article 12` in English and
the 24 expressions would never line up. The parser emits `Directive 2013/53/EU
art. 12` in all of them, and annexes become `Annex I` whatever the page says.

**The tagger is deterministic, not keyword-driven.** A keyword rule would have to
be written 24 times and would still tag the same provision differently in Dutch and
German. Instead `src/countries/eu_themes.py` maps *(act, article number)* → theme,
using ranges read off each act's own article titles. Themes:

`scope_definitions` · `craft_design` · `emissions` · `ce_marking` · `market_rules` ·
`vessel_certification` · `qualifications` · `final_provisions`

## Two renditions of the same act

EUR-Lex serves an act two ways and the parser reads both:

* the **Official Journal** rendition — paragraph text in `<p class="oj-normal">`
  under `oj-ti-art` headings;
* the **consolidated** rendition (the text in force) — paragraph text in
  `<div class="norm">` under `title-article-norm`.

Reading only one of them returns an article whose body is just its own heading, so
`_flatten` collects text nodes rather than any single tag.

**The fetcher prefers the consolidated text and falls back when it must.** EUR-Lex
does not serve the consolidated version with the ELI article skeleton in every
language — for Directive 2013/53/EU it is structured in EN and DE but a plain
unmarked page in NL and FR — and an unmarked page parses to *zero articles* rather
than to an error. So `fetch_eurlex` checks for the skeleton, falls back to the OJ
text when it is missing, and records which one it took (`text_status`:
`consolidated` | `as-published`) alongside the consolidation it did not use
(`latest_consolidated`). Nothing is swapped silently.

## Recitals are never ingested

A directive's recitals ("Whereas …") outnumber its articles and read like
provisions. They are the legislator's reasoning, not the enacted rule, so the parser
keeps only `art_N` subdivisions and the annexes. For the Recreational Craft
Directive that is 58 articles + 9 annexes, and 53 recitals dropped.

## Commands

```bash
python run.py build --country EU --lang en      # English (the default)
python run.py build --country EU --lang nl      # same acts, Dutch expression
```
