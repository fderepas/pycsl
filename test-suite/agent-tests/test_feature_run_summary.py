"""Test feature_supervisor.report.write_feature_run_summary (L4 rollout metrics)."""
import json
import sys
from pathlib import Path

_AGENTS = Path(__file__).resolve().parents[2] / "src" / "pycsl" / "agents"
sys.path.insert(0, str(_AGENTS))

from feature_supervisor import report as rep  # noqa: E402
from feature_supervisor.plan import Phase  # noqa: E402


def test_write_feature_run_summary(tmp_path, monkeypatch):
    monkeypatch.setattr(rep, "_HALT_REPORT_ROOT", tmp_path)
    phases = [
        Phase(number=0, title="done one", target_files=["x.py"],
              raw_body="**Level:** L5\n**Role:** Validator", status_done=True),
        Phase(number=1, title="open one", target_files=["y.py"],
              raw_body="**Level:** L2"),
    ]
    out = rep.write_feature_run_summary(
        Path("feat.md"), phases,
        exit_code=75, outcome="halted-ACCEPTANCE_FAILED",
        phase_outcomes={0: "STATUS_VERIFIED", 1: "FAIL"},
        accept_counts={0: {"total": 1, "passed": 1, "failed": 0},
                       1: {"total": 2, "passed": 0, "failed": 2}},
        gate_results=[],
        delegation_results=[],
        deny_hits=[(1, "y.py", "load-bearing")],
    )
    assert out is not None and out.exists()
    s = json.loads(out.read_text())
    assert s["outcome"] == "halted-ACCEPTANCE_FAILED"
    assert s["exit_code"] == 75
    p0, p1 = s["phases"]
    assert p0["level"] == "L5" and p0["role"] == "Validator"
    assert p0["outcome"] == "STATUS_VERIFIED"
    assert p1["level"] == "L2"
    assert p1["loadbearing_hits"] == 1
    assert p1["acceptance"] == {"total": 2, "passed": 0, "failed": 2}
    assert s["totals"]["verified"] == 1
    assert s["totals"]["failed"] == 1
    assert s["totals"]["loadbearing_hits"] == 1
