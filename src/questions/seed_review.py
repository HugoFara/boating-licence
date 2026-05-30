"""Durable ledger of *manual* review decisions.

The question bank (data/questions.sqlite) is regenerable and gitignored, so any
`review_status` set by hand would vanish on a destructive rebuild. Two of the
three generators already recover their status from committed inputs:

  * subagent drafts  -> data/verdicts/*.json        (verify-apply re-approves)
  * EN translations  -> data/translate_verdicts/*.json
  * figure questions -> auto_approved by the generator itself

Hand-authored seed questions (`seed:curated.v1`) and the occasional manual
override of a verdict straggler have no such record. This ledger fills that gap:
it stores every manual approve/reject by question id and re-applies them after a
rebuild, so the published bank is reproducible from committed inputs alone.

Scope on purpose: only ids decided by hand live here. Verdict-driven approvals
are deliberately NOT recorded, so a stale ledger entry can never override a
future change to a verdict. When both could speak to the same id, apply the
ledger LAST — a human decision is the final word.
"""

from __future__ import annotations

import json
import os

from . import schema as qschema

LEDGER = os.path.join(os.path.dirname(__file__), "..", "..", "data", "seed_review.json")
_DECISIONS = ("approved", "rejected")


def load() -> dict:
    """Return the ledger {question_id: 'approved'|'rejected'} (empty if absent)."""
    if not os.path.exists(LEDGER):
        return {}
    with open(LEDGER, encoding="utf-8") as fh:
        return json.load(fh)


def record(decisions: dict) -> dict:
    """Merge {id: status} into the ledger and persist (sorted, stable). Only
    approve/reject decisions are kept. Returns the full ledger."""
    led = load()
    led.update({k: v for k, v in decisions.items() if v in _DECISIONS})
    led = dict(sorted(led.items()))
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    with open(LEDGER, "w", encoding="utf-8") as fh:
        json.dump(led, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return led


def apply(conn) -> dict:
    """Re-apply recorded decisions to the bank. Ids absent from the bank update
    nothing. Returns {status: rows_updated}."""
    led = load()
    out = {}
    for status in _DECISIONS:
        ids = [qid for qid, s in led.items() if s == status]
        out[status] = qschema.set_review_status(conn, ids, status)
    return out
