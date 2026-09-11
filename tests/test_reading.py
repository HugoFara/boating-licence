"""Tests for the reading layer (src/questions/reading.py): the cited-article
bundle the player's Learn tab reads.

Covers: only units cited by exportable questions ship; the licence allow-list
gates verbatim text; a missing KB / unresolvable provenance ids yield no file.
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import schema as kbschema                                  # noqa: E402
from src.schema import KnowledgeUnit                                # noqa: E402
from src.questions import schema as qschema                         # noqa: E402
from src.questions.schema import Question, Choice, Provenance       # noqa: E402
from src.questions import reading                                   # noqa: E402


def _tmp(suffix):
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    return path


def _q(qid, unit_id, lang="fr", status="approved"):
    return Question(
        id=qid, theme="signalisation", kind="rule_mc", stem="Stem?",
        choices=[Choice("a", is_correct=True), Choice("b")],
        provenance=Provenance(unit_id=unit_id, ref="r", source="s", url="http://x"),
        review_status=status, lang=lang)


def _u(uid, licence, text="1 Il est interdit.2 La police.", lang="fr"):
    return KnowledgeUnit(
        id=uid, theme="signalisation", kind="article", ref=f"ONI art. {uid[-1]}",
        title="T", text=text, source_id="oni", source_name="ONI",
        source_url="https://fedlex/oni", retrieved="2026-01-01",
        legal_version="2025-01-01", licence=licence, lang=lang)


def _fixture():
    kb_path = _tmp(".sqlite")
    kb = kbschema.connect(kb_path)
    kbschema.write_units(kb, [
        _u("oni-1", "Public domain — Swiss federal law (freely reusable)."),
        _u("oni-2", "All rights reserved — publisher X."),      # not redistributable
        _u("oni-3", "Public domain — Swiss federal law (freely reusable)."),  # not cited
        _u("oni-4", "Public domain — Swiss federal law (freely reusable)."),  # cited by a draft only
        _u("oni-5", "CC BY-SA 4.0 — Wikipédia (FR), attribution required.", lang="fr"),
    ])
    kb.close()
    q_path = _tmp(".sqlite")
    qc = qschema.connect(q_path)
    qschema.write_questions(qc, [
        _q("q1", "oni-1"), _q("q2", "oni-1"),            # cited twice ⇒ once in the bundle
        _q("q3", "oni-2"),                               # cited, but licence blocks the text
        _q("q4", "oni-4", status="pending"),             # not exportable ⇒ not cited
        _q("q5", "oni-5", lang="en"),                    # cited only by the EN bank
        _q("q6", "elwis-zzz"),                           # provenance not a KB unit
    ])
    return qc, q_path, kb_path


def test_redistributable_allow_list():
    assert reading.redistributable("Public domain — Swiss federal law (freely reusable).")
    assert reading.redistributable("CC BY-SA 4.0 — Wikipedia (DE), attribution required.")
    assert reading.redistributable("Licence Ouverte / Open Licence 2.0 (Etalab) — …")
    assert reading.redistributable("Public domain — BSO (§5(1) UrhG / gemeinfrei).")
    assert not reading.redistributable("All rights reserved")
    assert not reading.redistributable("")
    assert not reading.redistributable(None)


def test_only_cited_exportable_redistributable_units_ship():
    qc, q_path, kb_path = _fixture()
    out = _tmp(".json")
    n = reading.export_reading_json(qc, kb_path, out, "fr")
    assert n == 1
    data = json.load(open(out, encoding="utf-8"))
    assert set(data["units"]) == {"oni-1"}
    u = data["units"]["oni-1"]
    assert u["text"].startswith("1 Il est interdit")       # verbatim, untouched
    assert u["licence"].startswith("Public domain")
    assert u["as_of"] == "2025-01-01"                       # legal_version wins over retrieved
    assert u["url"] == "https://fedlex/oni"
    assert data["meta"] == {"lang": "fr", "count": 1}
    # The EN bank cites a different (CC BY-SA) unit: shipped, attribution carried.
    n_en = reading.export_reading_json(qc, kb_path, out, "en")
    assert n_en == 1
    assert "attribution" in json.load(open(out, encoding="utf-8"))["units"]["oni-5"]["licence"]
    qc.close()
    for p in (q_path, kb_path, out):
        os.remove(p)


def test_no_kb_or_no_resolvable_ids_writes_nothing():
    qc, q_path, kb_path = _fixture()
    out = _tmp(".json")
    os.remove(out)
    # a language with no exportable questions
    assert reading.export_reading_json(qc, kb_path, out, "it") == 0
    assert not os.path.exists(out)
    # a KB that doesn't exist (country not built)
    assert reading.export_reading_json(qc, kb_path + ".missing", out, "fr") == 0
    assert not os.path.exists(out)
    qc.close()
    os.remove(q_path); os.remove(kb_path)
