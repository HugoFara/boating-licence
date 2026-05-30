"""Stage 3 — validate the *derived* common core against an official catalogue.

The German ELWIS bank is the project's one ground-truth-valid bank: it *is* the
amtliche Fragenkatalog. The CH and FR banks are *derived* from law, of unmeasured
fidelity. Because :mod:`src.scope` tags every question by harmonised base
(``universal``/``cevni``/``colregs``), the official German questions on a shared
base can act as a yardstick for the derived ones on the *same* base — the only
non-circular cross-check available (one side is official; the classifier restricts
the comparison to genuinely shared scope).

Two instruments, deliberately different in cost and confidence:

  * :func:`coverage` — deterministic, ``$0``, CI-friendly. Treats the official
    German shared-scope bank as a *checklist* of harmonised concepts and reports
    which concepts a derived bank under- or over-covers. It answers "is my derived
    inland core as broad as the official one?", never "is an answer right".

  * :func:`flag_divergences` — an on-demand **divergence flagger** (LLM). For a
    derived question matched to the official catalogue on a shared concept, it asks
    whether the derived keyed answer *contradicts* what the official catalogue
    establishes. It emits disagreements for a human to review — NOT a pass/fail
    score: the harmonised codes are harmonised, *not identical*, so a flag may be a
    legitimate national derogation rather than an error. Costs tokens; ``--deep``.

The concept checklist below is a deliberately auditable *starting point* (like the
keyword sets in :mod:`src.scope`): every concept names itself and carries the
harmonised base it belongs to. Extend it as the banks grow.
"""

from __future__ import annotations

import os
import re
import sqlite3
from dataclasses import dataclass

from . import scope
from .questions import schema as qschema

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

# The official ground-truth bank, and the derived banks it validates. Each maps to
# the SQLite file(s) that hold the built bank (a country may ship several tracks).
OFFICIAL = "DE"
BANK_FILES: dict[str, list[str]] = {
    "DE": ["questions.de.sqlite"],                       # official ELWIS catalogue
    "CH": ["questions.ch.sqlite"],                       # derived from Swiss law
    "FR": ["questions.fr_cotiere.sqlite",                # derived from French law
           "questions.fr_eaux_interieures.sqlite"],
}
# A CH question is stored once per content language (fr/de/it); DE and FR are
# single-language. Comparing raw counts would make CH look 3× as broad and would
# adjudicate every Swiss question three times — so each bank is collapsed to one
# comparison language (its canonical one). The flagger is cross-lingual anyway
# (the official side is always German), and the concept keywords match either tongue.
BANK_LANG: dict[str, str] = {"DE": "de", "CH": "fr", "FR": "fr"}


# --------------------------------------------------------------------------
# The harmonised concept checklist
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Concept:
    id: str
    base: str            # which harmonised base this concept lives on
    label: str
    pattern: "re.Pattern"


def _c(cid: str, base: str, label: str, *keywords: str) -> Concept:
    # One combined FR|DE(|IT) pattern per concept — a concept's French keywords
    # won't match German text and vice-versa, so the union matches each bank in its
    # own language without per-language bookkeeping.
    return Concept(cid, base, label,
                   re.compile("|".join(keywords), re.I))


# CEVNI — the harmonised INLAND code (DE-Binnen ⟷ CH inland / FR eaux intérieures).
# COLREGS — the harmonised MARITIME code (DE-See ⟷ FR côtière).
# Universal — portable seamanship shared by every track.
CONCEPTS: list[Concept] = [
    # --- CEVNI (inland) ---
    _c("blue_board", "cevni", "Blue board / overtaking sign",
       r"panneau bleu", r"flotteur bleu", r"blaue[rn]? (tafel|flagge)", r"bandiera blu"),
    _c("keep_right", "cevni", "Keep to the right / starboard side",
       r"rive droite", r"serrer (à|a) (tribord|droite)", r"rechte seite",
       r"rechts halten", r"steuerbordseite"),
    _c("sound_one_blast", "cevni", "Sound signal — one short blast",
       r"un son bref", r"ein kurzer ton", r"einen kurzen ton"),
    _c("lock_passage", "cevni", "Lock (écluse / Schleuse) passage",
       r"\b(é|e)cluse", r"\bschleuse", r"\bconca\b"),
    _c("buoyage_inland", "cevni", "Inland buoyage / fairway marks",
       r"chenal", r"bou(é|e)e", r"espar", r"fahrwasser", r"\btonne\b", r"schifffahrtszeichen"),
    _c("prohibition_sign", "cevni", "Prohibition sign",
       r"interdiction", r"interdit", r"verbot", r"verboten", r"divieto"),
    _c("wash_wave", "cevni", "Wash / wave-making duty",
       r"remous", r"batillage", r"wellenschlag", r"\bsog\b"),

    # --- COLREGS (maritime) ---
    _c("crossing_giveway", "colregs", "Crossing — give-way / stand-on",
       r"privil(é|e)gi(é|e)", r"route.*crois", r"ausweichpflicht", r"wegerecht",
       r"kurse.*kreuzen", r"kreuzende kurse"),
    _c("head_on", "colregs", "Head-on situation",
       r"face (à|a) face", r"\bde front\b", r"entgegengesetzt", r"genau.*entgegen"),
    _c("overtaking_sea", "colregs", "Overtaking at sea",
       r"rattrapant", r"d(é|e)passement", r"\b(ü|u)berhol"),
    _c("restricted_visibility", "colregs", "Restricted visibility",
       r"visibilit(é|e) r(é|e)duite", r"\bbrume\b", r"verminderte sicht",
       r"unsichtigem wetter", r"\bnebel\b"),
    _c("distress_signals", "colregs", "Distress signals",
       r"d(é|e)tresse", r"notzeichen", r"notsignal", r"seenot"),

    # --- Universal seamanship ---
    _c("knots", "universal", "Knots / matelotage",
       r"\bn(œ|oe)ud", r"\bknoten\b", r"palstek", r"\bstek\b", r"\bnodo\b"),
    _c("beaufort", "universal", "Beaufort scale / wind force",
       r"beaufort", r"windst(ä|a)rke"),
    _c("lifejacket", "universal", "Lifejacket",
       r"gilet de sauvetage", r"rettungsweste", r"giubbotto"),
]


# --------------------------------------------------------------------------
# Loading + scoping the banks
# --------------------------------------------------------------------------

def load_bank(code: str) -> list:
    """A country's built bank, collapsed to its single comparison language (see
    :data:`BANK_LANG`) so counts are one-per-logical-question across banks. Missing
    bank files are skipped (the bank may not be built locally)."""
    lang = BANK_LANG.get(code)
    out: list = []
    for fn in BANK_FILES.get(code, []):
        path = os.path.join(DATA, fn)
        if not os.path.exists(path):
            continue
        conn = qschema.connect(path)
        out += [q for q in qschema.load_questions(conn)
                if lang is None or getattr(q, "lang", lang) == lang]
        conn.close()
    return out


def _haystack(q) -> str:
    p = q.provenance
    return " ".join((q.stem or "", getattr(p, "ref", "") or "",
                     getattr(p, "source", "") or "")).lower()


def _base_questions(code: str) -> dict[str, list]:
    """The bank's questions bucketed by harmonised base (only the shareable
    universal/cevni/colregs scopes; national/local overlays are dropped)."""
    buckets: dict[str, list] = {b: [] for b in scope.BASES}
    for q in load_bank(code):
        s = scope.classify(q)
        if s in buckets:
            buckets[s].append(q)
    return buckets


# --------------------------------------------------------------------------
# Instrument 1 — deterministic coverage
# --------------------------------------------------------------------------

def coverage(derived: tuple[str, ...] = ("CH", "FR")) -> dict:
    """Compare each derived bank's harmonised-base coverage to the official one.

    Returns a report with (a) per-base question counts per bank and (b) a concept
    matrix: per concept, how many questions each bank carries, plus the *gaps* —
    concepts the official bank covers that a derived bank does not.
    """
    codes = [OFFICIAL, *derived]
    banks = {c: _base_questions(c) for c in codes}
    counts = {b: counts for c in codes
              for b, counts in [(c, {base: len(banks[c][base]) for base in scope.BASES})]}

    # A base the derived bank has *no* questions in is an absent *track*, not a
    # gap: Switzerland is inland-only, so its empty `colregs` is by design — we must
    # not nag it concept-by-concept for a maritime code it never implements. Such a
    # base is excluded from gap detection and reported separately.
    absent: list[dict] = []
    for c in derived:
        for base in scope.BASES:
            if counts[c][base] == 0 and counts[OFFICIAL][base] > 0:
                absent.append({"bank": c, "base": base})
    absent_pairs = {(a["bank"], a["base"]) for a in absent}

    matrix: list[dict] = []
    gaps: list[dict] = []
    for concept in CONCEPTS:
        row = {"concept": concept.id, "base": concept.base, "label": concept.label,
               "by_bank": {}}
        for c in codes:
            n = sum(1 for q in banks[c][concept.base]
                    if concept.pattern.search(_haystack(q)))
            row["by_bank"][c] = n
        matrix.append(row)
        off = row["by_bank"][OFFICIAL]
        for c in derived:
            if (c, concept.base) in absent_pairs:
                continue                          # whole track absent — not a gap
            if off > 0 and row["by_bank"][c] == 0:
                gaps.append({"bank": c, "concept": concept.id,
                             "base": concept.base, "label": concept.label,
                             "official_count": off})
    return {"codes": codes, "counts": counts, "matrix": matrix,
            "gaps": gaps, "absent_tracks": absent}


def format_coverage(report: dict) -> str:
    codes = report["codes"]
    lines = ["Harmonised-core coverage vs the official German catalogue", ""]
    # Base counts table.
    head = "  base        " + "".join(f"{c:>8}" for c in codes)
    lines += [head, "  " + "-" * (len(head) - 2)]
    for base in scope.BASES:
        lines.append("  " + f"{base:10}" + "  " +
                     "".join(f"{report['counts'][c][base]:>8}" for c in codes))
    # Concept matrix.
    lines += ["", "  concept (base)                 " + "".join(f"{c:>8}" for c in codes)]
    for row in report["matrix"]:
        label = f"{row['concept']} ({row['base']})"
        lines.append(f"  {label:30}" + "".join(f"{row['by_bank'][c]:>8}" for c in codes))
    # Absent tracks (by design — e.g. inland-only Switzerland has no maritime code).
    if report.get("absent_tracks"):
        lines += ["", "  tracks not implemented (excluded from gap detection):"]
        for a in report["absent_tracks"]:
            lines.append(f"    {a['bank']} has no {a['base']} questions "
                         f"(track absent by design)")
    # Gaps.
    if report["gaps"]:
        lines += ["", f"⚠ {len(report['gaps'])} coverage gap(s) — the official bank "
                      f"tests these harmonised concepts; the derived bank has none:"]
        for g in report["gaps"]:
            lines.append(f"    {g['bank']}: {g['concept']} ({g['base']}) — "
                         f"official has {g['official_count']}")
    else:
        lines += ["", "✓ No coverage gaps: every concept the official bank tests is "
                      "present in each derived bank."]
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Instrument 2 — on-demand LLM divergence flagger
# --------------------------------------------------------------------------

def _correct_texts(q) -> list[str]:
    return [ch.text for ch in q.choices if ch.is_correct]


def _q_brief(q) -> str:
    correct = " / ".join(_correct_texts(q)) or "(no key)"
    return f"Q: {q.stem}\n  keyed answer: {correct}"


_ADJUDICATE_SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string",
                    "enum": ["consistent", "diverges", "national_difference"]},
        "reason": {"type": "string"},
    },
    "required": ["verdict", "reason"],
}

_PROMPT = """You compare a DERIVED boat-licence exam question against an OFFICIAL \
catalogue on the SAME harmonised navigation rule ({base}: {label}).

The OFFICIAL catalogue (German ELWIS, ground truth) establishes this rule via:
{official}

The DERIVED question (from national law, fidelity unverified) is:
{derived}

Does the derived question's keyed answer CONTRADICT the harmonised rule the \
official catalogue establishes? Note: the inland (CEVNI) and maritime (COLREGS) \
codes are HARMONISED but not identical — a difference may be a legitimate national \
derogation, not an error. Reply with one of:
  - "consistent": the derived key agrees with the official rule.
  - "national_difference": they differ, but plausibly a real national derogation.
  - "diverges": the derived key appears WRONG against the harmonised rule.
Give a one-sentence reason."""


def _anthropic_adjudicator(model: str = "claude-sonnet-4-6"):
    import anthropic                              # lazy: importable without the SDK
    import json
    client = anthropic.Anthropic()

    def adjudicate(prompt: str) -> dict:
        msg = client.messages.create(
            model=model, max_tokens=400,
            tools=[{"name": "verdict", "description": "Emit the adjudication.",
                    "input_schema": _ADJUDICATE_SCHEMA}],
            tool_choice={"type": "tool", "name": "verdict"},
            messages=[{"role": "user", "content": prompt}])
        for block in msg.content:
            if getattr(block, "type", None) == "tool_use":
                return block.input
        raise RuntimeError("model returned no tool_use block")
    return adjudicate


def flag_divergences(derived_code: str, base: str = "cevni", limit: int = 20,
                     adjudicator=None, on_prompt=None) -> list[dict]:
    """Match derived questions to the official catalogue on a shared base+concept
    and ask the adjudicator whether each derived key contradicts the harmonised
    rule. Returns the non-"consistent" verdicts (the flags) for human review.

    `adjudicator` is a callable(prompt:str)->dict (so tests/dry-runs inject a fake,
    mirroring src.questions.prose). When None, the real Anthropic client is used.
    `on_prompt(prompt)` is called for each prompt before adjudication (for dry-run).
    """
    official_by_concept: dict[str, list] = {}
    for q in _base_questions(OFFICIAL)[base]:
        for concept in CONCEPTS:
            if concept.base == base and concept.pattern.search(_haystack(q)):
                official_by_concept.setdefault(concept.id, []).append(q)

    derived_buckets = _base_questions(derived_code)[base]
    if adjudicator is None and on_prompt is None:
        adjudicator = _anthropic_adjudicator()

    flags: list[dict] = []
    seen = 0
    for concept in CONCEPTS:
        if concept.base != base or concept.id not in official_by_concept:
            continue
        for dq in derived_buckets:
            if seen >= limit:
                return flags
            if not concept.pattern.search(_haystack(dq)):
                continue
            seen += 1
            official = "\n".join(f"  - {_q_brief(oq)}"
                                 for oq in official_by_concept[concept.id][:3])
            prompt = _PROMPT.format(base=base, label=concept.label,
                                    official=official, derived=_q_brief(dq))
            if on_prompt is not None:
                on_prompt(prompt)
                continue
            v = adjudicator(prompt)
            if v.get("verdict") != "consistent":
                flags.append({"bank": derived_code, "concept": concept.id,
                              "question_id": dq.id, "stem": dq.stem,
                              "verdict": v.get("verdict"), "reason": v.get("reason")})
    return flags
