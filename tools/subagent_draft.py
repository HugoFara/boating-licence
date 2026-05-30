"""Draft prose questions with *subagents* instead of the Anthropic API.

Same pipeline as `src/questions/prose.py` (select → prompt → parse → grounding →
validate → pending → review), but the drafting and the verification are done by
Claude subagents driven from the chat loop, with files as the hand-off. Stages:

  emit          select FR prose units per theme  -> data/draft_jobs.json
  (subagents)   draft per theme, write           -> data/draft_answers/<theme>.json
  ingest        parse+ground+validate, write pending questions to the bank
  verify-emit   dump each pending draft + its source text -> data/verify_jobs.json
  (subagents)   adversarially verify, write       -> data/verdicts.json  {qid: pass|fail}
  verify-apply  approve the verified drafts (rest stay pending for human review)

Everything is grounded in public-domain ONI/RNL text; the verification pass is an
independent check (a different agent, told to default to FAIL) before approval.
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.questions import prose                       # noqa: E402
from src.questions import schema as qschema           # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB_PATH = os.path.join(BASE, "data", "kb.sqlite")
QDB_PATH = os.path.join(BASE, "data", "questions.sqlite")
JOBS = os.path.join(BASE, "data", "draft_jobs.json")
ANSWERS_DIR = os.path.join(BASE, "data", "draft_answers")
VERIFY_JOBS = os.path.join(BASE, "data", "verify_jobs.json")
VERDICTS = os.path.join(BASE, "data", "verdicts.json")

GENERATOR = "subagent:fr.v1"
MIN_GROUNDING = 0.34

# Per-theme (unit count, questions-per-unit). Tuned to the available FR pool and
# aiming for ~10 surviving questions per theme for a balanced 6-theme exam.
PLAN = {
    "definitions": (2, 3),
    "meteorologie": (6, 2),
    "matelotage": (6, 2),
    "eaux_frontalieres": (6, 2),
    "lois": (8, 2),
}


def _kb():
    return sqlite3.connect(KB_PATH)


def cmd_emit():
    kb = _kb()
    jobs = {}
    for theme, (n_units, per_unit) in PLAN.items():
        units = prose.select_units(kb, theme, limit=n_units, lang="fr")
        for u in units:
            u["_per_unit"] = per_unit
        jobs[theme] = units
        print(f"  {theme:18} {len(units)} units × {per_unit} q")
    with open(JOBS, "w", encoding="utf-8") as fh:
        json.dump(jobs, fh, ensure_ascii=False, indent=2)
    os.makedirs(ANSWERS_DIR, exist_ok=True)
    print(f"→ {JOBS}")


def cmd_ingest():
    jobs = json.load(open(JOBS, encoding="utf-8"))
    conn = qschema.connect(QDB_PATH)
    grand = {"drafted": 0, "kept": 0, "invalid": 0, "weak_grounding": 0, "no_answer": 0}
    for theme, units in jobs.items():
        by_ref = {u["ref"]: u for u in units}
        path = os.path.join(ANSWERS_DIR, f"{theme}.json")
        if not os.path.exists(path):
            print(f"  {theme:18} (no answers file — skipped)")
            continue
        data = json.load(open(path, encoding="utf-8"))
        drafts = data["drafts"] if isinstance(data, dict) else data
        kept_q, st = [], {"drafted": 0, "kept": 0, "invalid": 0, "weak_grounding": 0}
        for d in drafts:
            unit = by_ref.get(d.get("ref"))
            if unit is None:
                grand["no_answer"] += 1
                continue
            unit["_generator"] = GENERATOR
            qs = prose.parse_drafts(json.dumps({"questions": d["questions"]}), unit)
            for q in qs:
                st["drafted"] += 1
                if qschema.validate(q):
                    st["invalid"] += 1
                    continue
                correct = " ".join(c.text for c in q.choices if c.is_correct)
                if prose.grounding_score(correct, unit["text"]) < MIN_GROUNDING:
                    st["weak_grounding"] += 1
                    continue
                kept_q.append(q)
                st["kept"] += 1
        qschema.write_questions(conn, kept_q)
        for k in ("drafted", "kept", "invalid", "weak_grounding"):
            grand[k] += st[k]
        print(f"  {theme:18} drafted {st['drafted']:3}  kept {st['kept']:3}  "
              f"invalid {st['invalid']}  weak {st['weak_grounding']}")
    print(f"→ pending written. totals: {grand}")
    print("  review queue:", qschema.counts_by_status(conn))


def cmd_verify_emit():
    """Dump every pending subagent draft with its source text for verification."""
    conn = qschema.connect(QDB_PATH)
    conn.row_factory = sqlite3.Row
    kb = _kb()
    kb.row_factory = sqlite3.Row
    out = []
    rows = conn.execute(
        "SELECT * FROM questions WHERE review_status='pending' AND generator=? "
        "ORDER BY theme, id", (GENERATOR,)).fetchall()
    for r in rows:
        src = kb.execute("SELECT text FROM units WHERE id=?",
                         (r["prov_unit_id"],)).fetchone()
        choices = [{"text": c["text"], "correct": bool(c["is_correct"])}
                   for c in conn.execute(
                       "SELECT text, is_correct FROM choices WHERE question_id=? "
                       "ORDER BY idx", (r["id"],))]
        out.append({"qid": r["id"], "theme": r["theme"], "ref": r["prov_ref"],
                    "stem": r["stem"], "polarity": r["polarity"],
                    "choices": choices, "source_text": src["text"] if src else ""})
    with open(VERIFY_JOBS, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print(f"→ {VERIFY_JOBS} ({len(out)} drafts to verify)")


def cmd_verify_apply():
    verdicts = json.load(open(VERDICTS, encoding="utf-8"))
    conn = qschema.connect(QDB_PATH)
    passed = [qid for qid, v in verdicts.items() if str(v).lower().startswith("pass")]
    n = qschema.set_review_status(conn, passed, "approved")
    print(f"  approved {n} verified drafts")
    failed = [qid for qid, v in verdicts.items() if not str(v).lower().startswith("pass")]
    print(f"  left pending (failed/uncertain): {len(failed)}")
    print("  review queue:", qschema.counts_by_status(conn))


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    fns = {"emit": cmd_emit, "ingest": cmd_ingest,
           "verify-emit": cmd_verify_emit, "verify-apply": cmd_verify_apply}
    if cmd not in fns:
        sys.exit(f"usage: python tools/subagent_draft.py {{{'|'.join(fns)}}}")
    fns[cmd]()


if __name__ == "__main__":
    main()
