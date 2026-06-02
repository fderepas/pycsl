"""Tests for the coordinator's CMMI-L4 per-file run-summary (metrics/run-summary/).

Covers the reconciliation diagnostic-accuracy DOWNSTREAM PROXY (a recommendation
is "right" iff the next attempt's proof passes), the loop counters, and the Rocq
marker parsing.
"""
import json
import sys
from pathlib import Path

_AGENTS = Path(__file__).resolve().parents[2] / "src" / "pycsl" / "agents"
sys.path.insert(0, str(_AGENTS))

import coordinator as co  # noqa: E402


def _setup(tmp_path):
    (tmp_path / "tests" / "to_annotate").mkdir(parents=True)
    (tmp_path / "tests" / "to_annotate" / "0001.py").write_text(
        "def f():\n    return 0\n", encoding="utf-8")
    return co.CoordinatorAgent(tmp_path)


def _base_mocks(ag, monkeypatch):
    monkeypatch.setattr(ag, "annotate_file", lambda tf: True)
    monkeypatch.setattr(ag, "run_meta_evaluator", lambda *a, **k: None)
    monkeypatch.setattr(ag, "run_meta_monitor", lambda *a, **k: None)
    monkeypatch.setattr(ag, "run_meta_reviewer", lambda *a, **k: None)


def _summary(tmp_path):
    return json.loads((tmp_path / "metrics" / "run-summary" / "0001.json").read_text())


def test_parse_rocq_marker():
    p = co.CoordinatorAgent._parse_rocq_marker
    assert p('noise\nROCQ-SUMMARY {"retries": 2, "status": "completed"}\n', 0) == (2, "completed")
    assert p('ROCQ-SUMMARY {"retries": 1, "status": "aborted"}', 1) == (1, "aborted")
    # no marker -> fall back to exit code
    assert p("nothing here", 0) == (None, "completed")
    assert p("nothing here", 1) == (None, "incomplete")


def test_subactor_correct_cause_is_scored(tmp_path, monkeypatch):
    """fail -> sub-actor reconcile -> apply -> next attempt passes => right_cause True."""
    ag = _setup(tmp_path)
    _base_mocks(ag, monkeypatch)
    n = {"pycsl": 0}
    monkeypatch.setattr(ag, "run_pycsl_file",
                        lambda af: (n.__setitem__("pycsl", n["pycsl"] + 1) or n["pycsl"] >= 2))
    monkeypatch.setattr(ag, "reconcile_failure", lambda *a, **k: (
        {"language": "python", "author": "a", "recommendation": "fix it",
         "target": "update-pycsl-scripts", "fault_class": "sub-actor"},
        tmp_path / "r.log"))
    monkeypatch.setattr(ag, "apply_recommendations", lambda *a, **k: (True, []))

    rc = ag.run()
    assert rc == 0
    s = _summary(tmp_path)
    assert s["outcome"] == "passed"
    assert s["attempts_used"] == 2
    assert s["attempts"][0]["right_cause"] is True
    assert s["attempts"][0]["action"]["kind"] == "script-update"
    assert s["fault_correctness"]["overall"] == {"correct": 1, "total": 1}
    assert s["fault_correctness"]["by_class"]["sub-actor"]["correct"] == 1


def test_specifier_redecompose_scored(tmp_path, monkeypatch):
    """fail -> specifier reconcile -> redecompose -> next attempt passes => right_cause True."""
    ag = _setup(tmp_path)
    _base_mocks(ag, monkeypatch)
    n = {"pycsl": 0}
    monkeypatch.setattr(ag, "run_pycsl_file",
                        lambda af: (n.__setitem__("pycsl", n["pycsl"] + 1) or n["pycsl"] >= 2))
    monkeypatch.setattr(ag, "reconcile_failure", lambda *a, **k: (
        {"language": "python", "author": "a", "recommendation": "redecompose",
         "target": "error-in-annotations", "fault_class": "specifier"},
        tmp_path / "r.log"))
    monkeypatch.setattr(ag, "redecompose_at_l4", lambda *a, **k: True)

    rc = ag.run()
    assert rc == 0
    s = _summary(tmp_path)
    assert s["attempts"][0]["action"]["kind"] == "redecompose"
    assert s["attempts"][0]["right_cause"] is True
    assert s["loop"]["redecompose_count"] == 1
    # rate is added at ingest time; the run-summary carries correct/total.
    assert s["fault_correctness"]["by_class"]["specifier"] == {"correct": 1, "total": 1}


def test_max_retries_summary_records_loop_and_rocq(tmp_path, monkeypatch):
    """Never passes -> exit 72, run-summary records the attempts + Rocq accounting."""
    ag = _setup(tmp_path)
    _base_mocks(ag, monkeypatch)
    monkeypatch.setattr(ag, "run_pycsl_file", lambda af: False)
    n = {"i": 0}
    # Distinct recommendation text each attempt → no loop-detect (exit 73);
    # the loop runs to max retries (exit 72).
    monkeypatch.setattr(ag, "reconcile_failure", lambda *a, **k: (
        n.__setitem__("i", n["i"] + 1) or
        {"language": "python", "author": "a", "recommendation": f"fix {n['i']}",
         "target": "update-pycsl-scripts", "fault_class": "sub-actor"},
        tmp_path / "r.log"))
    monkeypatch.setattr(ag, "apply_recommendations", lambda *a, **k: (True, []))
    monkeypatch.setattr(ag, "write_ncr", lambda **k: None)
    monkeypatch.setattr(ag, "attempt_rocq_proof",
                        lambda af: (False, {"generated": 2, "completed": 1, "aborted": 0,
                                            "incomplete": 1, "obligations": []}))
    rc = ag.run()
    assert rc == co.EXIT_MAX_RETRIES
    s = _summary(tmp_path)
    assert s["outcome"] == "max-retries"
    assert s["exit_code"] == 72
    assert s["ncr_emitted"] is True
    assert s["rocq"]["generated"] == 2 and s["rocq"]["completed"] == 1
