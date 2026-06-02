"""Tests for the coordinator's cross-level (L5->L4) reconciliation routing.

A reconcile fault_class of "specifier" means the file's *decomposition* is wrong,
not this unit's body — the coordinator must escalate to L4 (re-decompose via
agent-splitter) instead of re-patching the unit, bounded by MAX_REDECOMPOSE to
stop L5<->L4 ping-pong. "sub-actor" (the default) keeps the existing per-unit fix.

The retry loop is driven with all side-effecting collaborators mocked.
"""
import sys
from pathlib import Path

import pytest

_AGENTS = Path(__file__).resolve().parents[2] / "src" / "pycsl" / "agents"
sys.path.insert(0, str(_AGENTS))

import coordinator as co  # noqa: E402


def _setup(tmp_path):
    (tmp_path / "tests" / "to_annotate").mkdir(parents=True)
    (tmp_path / "tests" / "to_annotate" / "0001.py").write_text(
        "def f():\n    return 0\n", encoding="utf-8")
    return co.CoordinatorAgent(tmp_path)


def _common_mocks(ag, monkeypatch, calls, *, fault_class, target):
    """pycsl always fails; reconcile returns a DISTINCT recommendation each attempt
    (distinct text keeps the 3-strike loop-detector quiet so we exercise routing)."""
    n = {"i": 0}
    monkeypatch.setattr(ag, "annotate_file", lambda tf: True)
    monkeypatch.setattr(ag, "run_pycsl_file", lambda af: False)

    def fake_reconcile(af, out_std, out_err, ret_code, attempt):
        n["i"] += 1
        return {
            "language": "python", "author": "a",
            "recommendation": f"fix {n['i']}",
            "target": target, "fault_class": fault_class,
        }, tmp_log(ag)
    monkeypatch.setattr(ag, "reconcile_failure", fake_reconcile)
    monkeypatch.setattr(ag, "apply_recommendations",
                        lambda *a, **k: (calls.__setitem__("apply", calls["apply"] + 1) or (True, [])))

    def fake_redecompose(tf, af, attempt):
        calls["redecompose"] += 1
        return True
    monkeypatch.setattr(ag, "redecompose_at_l4", fake_redecompose)
    monkeypatch.setattr(ag, "attempt_rocq_proof", lambda *a, **k: False)
    monkeypatch.setattr(ag, "run_meta_monitor", lambda *a, **k: None)
    monkeypatch.setattr(ag, "run_meta_reviewer", lambda *a, **k: None)
    monkeypatch.setattr(ag, "run_meta_evaluator", lambda *a, **k: None)
    monkeypatch.setattr(ag, "write_ncr",
                        lambda **k: (calls["ncr"].append(k) or (Path("/tmp/ncr.md"))))


def tmp_log(ag):
    return ag.metrics_dir / "logs" / "r.log"


def test_subactor_fault_uses_apply_not_redecompose(tmp_path, monkeypatch):
    ag = _setup(tmp_path)
    calls = {"apply": 0, "redecompose": 0, "ncr": []}
    _common_mocks(ag, monkeypatch, calls, fault_class="sub-actor", target="update-pycsl-scripts")
    rc = ag.run()
    assert rc == co.EXIT_MAX_RETRIES
    assert calls["redecompose"] == 0          # never escalated to L4
    assert calls["apply"] >= 1                # per-unit fix path used
    assert calls["ncr"][-1]["exit_code"] == co.EXIT_MAX_RETRIES


def test_specifier_fault_redecomposes_then_pingpong_halts(tmp_path, monkeypatch):
    ag = _setup(tmp_path)
    calls = {"apply": 0, "redecompose": 0, "ncr": []}
    _common_mocks(ag, monkeypatch, calls, fault_class="specifier", target="error-in-annotations")
    rc = ag.run()
    assert rc == co.EXIT_LOOP_DETECTED
    # MAX_REDECOMPOSE successful escalations, then the next specifier fault halts
    assert calls["redecompose"] == co.MAX_REDECOMPOSE
    assert calls["apply"] == 0                # specifier faults never re-patch the unit
    assert calls["ncr"], "ping-pong halt must emit an NCR"
    assert "ping-pong" in calls["ncr"][-1].get("finding", "")
    assert calls["ncr"][-1]["exit_code"] == co.EXIT_LOOP_DETECTED


def test_ncr_emitted_before_reviewer(tmp_path, monkeypatch):
    """The NCR is a deterministic artifact: it must be written before (and
    independent of) the LLM meta-reviewer, so a reviewer failure can't suppress it."""
    ag = _setup(tmp_path)
    calls = {"apply": 0, "redecompose": 0, "ncr": []}
    _common_mocks(ag, monkeypatch, calls, fault_class="sub-actor", target="update-pycsl-scripts")

    def boom(*a, **k):
        raise RuntimeError("reviewer down")
    monkeypatch.setattr(ag, "run_meta_reviewer", boom)

    with pytest.raises(RuntimeError):
        ag.run()
    assert calls["ncr"], "NCR must already be emitted when the reviewer fails"


def test_redecompose_invokes_agent_splitter(tmp_path, monkeypatch):
    ag = _setup(tmp_path)
    seen = {}

    def fake_run(cmd, **k):
        import subprocess
        seen["cmd"] = [str(c) for c in cmd]
        return subprocess.CompletedProcess(cmd, 0, "", "")
    monkeypatch.setattr(ag, "run_command", fake_run)

    ok = ag.redecompose_at_l4(
        tmp_path / "tests" / "to_annotate" / "0001.py",
        tmp_path / "tests" / "annotated" / "0001.py", 0)
    assert ok
    assert any("agent-splitter.py" in c for c in seen["cmd"])
    assert "--in" in seen["cmd"] and "--out" in seen["cmd"]
