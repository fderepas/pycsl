"""Tests for the coordinator's Workflow-3 NCR artifact (exit 72/73).

The coordinator halts when the annotate->prove->reconcile loop cannot converge.
Per cmmi-glue Workflow 3 it must emit a Non-Conformance Report — a deterministic,
schema-conforming governance artifact (NOT the LLM meta-reviewer) that feeds the
escalation chain `coordinator exit 72/73 -> agent-meta-monitor ->
agent-feature-supervisor -> human` (bound in cmmi-glue/SKILL.md).
"""
import json
import sys
from pathlib import Path

_AGENTS = Path(__file__).resolve().parents[2] / "src" / "pycsl" / "agents"
sys.path.insert(0, str(_AGENTS))

import coordinator as co  # noqa: E402
import schema_validator  # noqa: E402


def _embedded_ncr(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    blob = text.split("```json", 1)[1].split("```", 1)[0]
    return json.loads(blob)


def test_exit73_ncr_validates_and_traces(tmp_path):
    ag = co.CoordinatorAgent(tmp_path)
    rec = {
        "language": "python", "author": "a",
        "recommendation": "add loop invariant",
        "target": "error-in-annotations", "fault_class": "specifier",
    }
    p = ag.write_ncr(
        exit_code=co.EXIT_LOOP_DETECTED,
        annotated_file=Path("tests/annotated/0001.py"),
        recommendation=rec, attempt=4, consecutive=2,
        log_paths=[Path("metrics/logs/reconcile_0001_4.log")],
    )
    assert p is not None and p.exists()
    ncr = _embedded_ncr(p)
    assert schema_validator.validate(ncr, "ncr") == [], ncr
    assert ncr["evidence"]["exit_code"] == 73
    assert ncr["evidence"]["consecutive_identical"] == 2
    assert ncr["evidence"]["retry_count"] == 5
    assert ncr["status"] == "OPEN"
    assert ncr["gate_failed"] == "Gate 1"
    # Traceable to the cmmi-glue Workflow-3 chain
    assert "Workflow 3" in ncr["escalation_path"]
    assert "agent-meta-monitor" in ncr["escalation_path"]
    assert "agent-feature-supervisor" in ncr["escalation_path"]
    # error-in-annotations routes to the Specifier role
    assert ncr["responsible_role"].startswith("Specifier")


def test_exit72_ncr_validates(tmp_path):
    ag = co.CoordinatorAgent(tmp_path)
    rec = {
        "language": "python", "author": "a",
        "recommendation": "emit Map preamble",
        "target": "update-pycsl-scripts", "fault_class": "sub-actor",
    }
    p = ag.write_ncr(
        exit_code=co.EXIT_MAX_RETRIES,
        annotated_file=Path("0002.py"),
        recommendation=rec, attempt=10, consecutive=None,
    )
    ncr = _embedded_ncr(p)
    assert schema_validator.validate(ncr, "ncr") == [], ncr
    assert ncr["evidence"]["exit_code"] == 72
    assert ncr["evidence"]["consecutive_identical"] is None
    assert ncr["evidence"]["retry_count"] == 11
    # update-pycsl-scripts routes to the sub-actor role
    assert ncr["responsible_role"].startswith("Sub-actor")


def test_ncr_emitted_with_no_recommendation(tmp_path):
    ag = co.CoordinatorAgent(tmp_path)
    p = ag.write_ncr(
        exit_code=co.EXIT_MAX_RETRIES,
        annotated_file=Path("0003.py"),
        recommendation=None, attempt=10,
    )
    ncr = _embedded_ncr(p)
    assert schema_validator.validate(ncr, "ncr") == [], ncr
    assert ncr["responsible_role"] == "Unknown"
    assert ncr["evidence"]["recurring_recommendation"] is None
