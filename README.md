# Boat-permit — free study tool for the Swiss cat-A motorboat theory exam

A free, open study tool for the **Swiss category-A motorboat theory exam**
(Geneva / OCV, Lac Léman). It is built **only** from public-domain law and
clearly-reusable references, and it ships two things:

1. a structured, versioned **knowledge base** (KB) derived from the law, and
2. a **practice-question bank** (`questions.json`) plus a small **static player**
   you can open in a browser or host on GitHub Pages.

## Legal boundary (the whole point)

The official exam draws on an **asa-licensed** ~520-question bank, repackaged by
the paid prep apps (BoatDriver, iTheorie, theorie-bateau, …). This project
deliberately **does not touch any of that**.

- **It ingests:** the ONI and other federal/cantonal navigation law (Swiss
  federal law is public-domain and freely reusable), plus freely-licensed météo
  and matelotage references. Provenance + a licence note are stored on every unit.
- **It never scrapes, stores, or reproduces:** the asa question bank, or any paid
  app's questions/explanations.

Every practice question is **derived from primary sources** and carries a citation
back to the article or figure it came from.

## Quick start

```bash
pip install -r requirements.txt

python run.py build        # fetch + parse + normalize law -> data/kb.sqlite (+ kb.json)
python run.py questions    # derive templated figure questions -> data/questions.sqlite
python run.py web          # bundle the approved bank + assets into web/

# then open the player:
python -m http.server -d web 8000   # http://localhost:8000
```

The KB build is cached and re-runnable; `--force` re-fetches everything. The
question and web steps are pure transforms over the previous outputs.

## How it works

### Phase 1 — knowledge base (`run.py build`)

Three independently re-runnable stages, each reading the previous one's output:

| Stage | Command | What it does |
|-------|---------|--------------|
| **Fetch** | `python run.py fetch` | Pulls raw sources into `data/raw/<id>/`, verbatim, with a `manifest.json` recording URL + retrieval date + legal version. Never re-fetches unless `--force`. |
| **Parse** | `python run.py parse` | Turns each raw source into structured `KnowledgeUnit`s (pure, no network). One parser per source type. |
| **Normalize** | (part of `build`) | Merges into one SQLite KB, localizes image assets, links articles ↔ figures, tags every unit to an exam theme, stamps a version. |

Limit to specific sources with `--only oni,rnl`. The current KB holds **602
units** across articles, annex figures, and prose sections.

**Law fetch:** Fedlex pages are JS-rendered, so we never scrape the page HTML.
We resolve the **Akoma Ntoso XML** (article text) and its referenced annex images
via the Fedlex **SPARQL endpoint** + filestore. The XML images carry the
signalisation diagrams (lights, buoys, boards), captioned from their annex tables
(181/181 figures captioned, linked to the citing articles).

### Phase 2 — question bank + player

| Step | Command | What it does |
|------|---------|--------------|
| **Figures** | `python run.py questions` | Deterministically generates figure-recognition questions from the captioned annex diagrams. Confusion-set distractors keyed by signal type; sha1-seeded so the output is stable. Auto-approved. |
| **Draft** | `python run.py draft --theme … ` | Drafts prose questions with an LLM, strictly source-grounded (a lexical grounding guard drops likely hallucinations). Lands in the bank as **`pending`**. Needs an API key — see `requirements.txt`. A built-in **seed set** of hand-authored questions is available via `--seed`. |
| **Review** | `python run.py review --list / --approve / --reject` | Human review gate. Only `auto_approved` + `approved` questions are ever exported. |
| **Web** | `python run.py web` | Re-exports the approved bank to `questions.json` and bundles it with the figure assets into `web/`. |

The bank currently exports **73 reviewed questions** (71 templated figures + an
approved seed pair), with more prose questions sitting behind the review gate.

**The player** (`web/`) is dependency-free vanilla JS. It loads `questions.json`,
reads the exam config from its `meta`, and runs two modes: a chronometered **exam**
(60 questions, balanced across themes) and a **practice** mode with source-cited
corrections. Scoring mirrors the real exam exactly.

### Exam format (verified against official VKS / OCV sources)

**60 questions · 50 minutes · 180 points · pass at 165/180** (max 15 fault points,
≈ 5 fully-wrong questions). Each question has 3 answers of which **1–2 are correct**
(multi-select), scored **all-or-nothing** per question (3 pts only if the selected
set matches exactly). The exam is standardized intercantonally by the VKS; Geneva's
OCV administers this national standard. The 50-minute timer is the one cantonal
detail (Bern uses 45).

## Sources

| id | Source | Themes | Licence tier |
|----|--------|--------|--------------|
| `oni` | ONI — Ordonnance sur la navigation intérieure (RS 747.201.1) | Définitions, Lois, Signalisation (+ annexe figures) | public domain |
| `rnl` | Règlement de la navigation sur le Léman (RS 747.221.1) | Eaux frontalières, Signalisation | public domain |
| `matelotage_wp` | Wikipédia — nœuds marins | Matelotage | CC BY-SA 4.0 |
| `meteo_vents` | MétéoSuisse — Les vents du Léman | Météorologie | official, attribute |
| `meteo_signaux` | SISL — signaux d'avis de tempête | Météorologie / Signalisation | cross-check only |
| `geneve` | Genève — consignes générales de navigation | Lois (cantonal) | official, attribute |

## Exam theme taxonomy (normalization target)

1. Définitions · 2. Météorologie · 3. Lois sur la navigation en eaux intérieures ·
4. Signalisation et signaux acoustiques · 5. Matelotage · 6. Eaux frontalières

Tagging is rule-based and auditable (source default + keyword heuristics over
`ref`/`title`/`text`); see `src/themes.py`. It is intentionally easy to tune.

## Layout

```
run.py                 CLI orchestrator (build / questions / draft / review / web)
src/
  sources.py           approved source registry (provenance + licence)
  fetch.py             stage 1 — fetch + cache (Fedlex SPARQL, MediaWiki API, HTTP)
  parse.py             stage 2 — dispatch to parsers
  parsers/             Akoma Ntoso law, MediaWiki prose, generic HTML
  normalize.py         stage 3 — merge -> SQLite + asset localization
  schema.py            KnowledgeUnit + SQLite DDL + JSON export
  themes.py            exam taxonomy + tagging rules
  questions/
    schema.py          canonical question schema, scoring, review gate, JSON export
    figures.py         templated figure-recognition generator
    prose.py           LLM-draft pipeline + grounding guard
    seed_prose.py      hand-authored seed questions
web/                   dependency-free static player (index.html, app.js, style.css)
tests/                 plain-assert tests (run: python tests/test_*.py)
data/                  generated (gitignored): raw cache, assets, *.sqlite, *.json
```

## Tests

```bash
for t in tests/test_*.py; do python "$t"; done
```

All offline; no network or API key needed.

## Licence

Tooling in this repo is open for reuse. Ingested content keeps its own licence,
recorded per unit (see the Sources table). Federal/cantonal law is public-domain;
Wikipedia matelotage material is CC BY-SA 4.0; météo/cantonal pages are official
sources used with attribution.
