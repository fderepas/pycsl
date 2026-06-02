"""Test bin/cmmi-metrics-ingest.py collect_agent_loop_kpis aggregation.

Writes synthetic run-summary + feature-run-summary artifacts into a tmp metrics
tree and checks the rolled-up CMMI-L4 KPIs (rates, means, by-class correctness).
"""
import importlib.util as iu
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_BIN = _REPO / "bin" / "cmmi-metrics-ingest.py"


def _load_ingest():
    spec = iu.spec_from_file_location("cmmi_metrics_ingest", _BIN)
    m = iu.module_from_spec(spec)
    sys.modules["cmmi_metrics_ingest"] = m
    spec.loader.exec_module(m)
    return m


def _write(p: Path, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj), encoding="utf-8")


def test_collect_agent_loop_kpis(tmp_path, monkeypatch):
    m = _load_ingest()
    metrics = tmp_path / "metrics"
    monkeypatch.setattr(m, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(m, "METRICS_SRC", metrics)

    _write(metrics / "run-summary" / "A.json", {
        "file": "A.py", "outcome": "passed", "attempts_used": 2, "attempts": [],
        "loop": {"redecompose_count": 0},
        "fault_correctness": {"by_class": {"sub-actor": {"correct": 1, "total": 1}},
                              "overall": {"correct": 1, "total": 1}},
        "rocq": None, "ncr_emitted": False,
    })
    _write(metrics / "run-summary" / "B.json", {
        "file": "B.py", "outcome": "max-retries", "attempts_used": 11, "attempts": [],
        "loop": {"redecompose_count": 1},
        "fault_correctness": {"by_class": {"specifier": {"correct": 0, "total": 2}},
                              "overall": {"correct": 0, "total": 2}},
        "rocq": {"generated": 3, "completed": 2, "aborted": 1, "incomplete": 0,
                 "obligations": [{"retries": 1}, {"retries": 3}]},
        "ncr_emitted": True,
    })
    _write(metrics / "feature-supervisor" / "feat" / "run-summary.json", {
        "feature_file": "f.md", "slug": "feat", "outcome": "green",
        "phases": [
            {"number": 0, "outcome": "PASS", "acceptance": {"total": 1, "passed": 1, "failed": 0}},
            {"number": 1, "outcome": "FAIL", "acceptance": {"total": 1, "passed": 0, "failed": 1}},
        ],
        "gate": [{"step": "a", "passed": True, "skipped": False},
                 {"step": "b", "passed": False, "skipped": False}],
        "totals": {"delegated": 0, "rolled_back": 0},
    })

    k = m.collect_agent_loop_kpis()
    al = k["annotation_loop"]
    assert al["files"] == 2
    assert al["convergence_attempts"] == {"avg": 6.5, "max": 11, "samples": 2}
    assert al["redecompose_rate"] == 0.5
    assert al["first_fix_yield"] == 0.5            # A passed at 2 attempts; B needed reconcile
    assert al["fault_correctness"]["overall"]["rate"] == round(1 / 3, 4)
    assert al["fault_correctness"]["by_class"]["sub-actor"]["rate"] == 1.0
    assert al["fault_correctness"]["by_class"]["specifier"]["rate"] == 0.0
    assert al["rocq"]["completion_rate"] == round(2 / 3, 4)
    assert al["rocq"]["abort_rate"] == round(1 / 3, 4)
    assert al["rocq"]["retries"] == {"avg": 2.0, "max": 3, "samples": 2}

    fr = k["feature_rollout"]
    assert fr["runs"] == 1
    assert fr["acceptance_passrate"] == 0.5
    assert fr["gate_passrate"] == 0.5
    assert fr["delegation_rollback_rate"] is None   # 0 delegated
    assert fr["loadbearing_halt_rate"] == 0.0
