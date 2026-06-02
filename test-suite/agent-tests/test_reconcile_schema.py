"""Schema-contract tests for the reconcile output after adding fault_class.

agent-reconcile now classifies each failure's fault_class (the L5->L4 routing
signal the coordinator consumes). The schema must require it, constrain it to the
enum, and stay closed (additionalProperties:false). Validation requires the
jsonschema library to exercise enum/closed-object rules.
"""
import sys
from pathlib import Path

import pytest

_AGENTS = Path(__file__).resolve().parents[2] / "src" / "pycsl" / "agents"
sys.path.insert(0, str(_AGENTS))

import schema_validator  # noqa: E402

jsonschema = pytest.importorskip("jsonschema")

_BASE = {
    "language": "python", "author": "a",
    "recommendation": "fix it", "target": "error-in-annotations",
}


def test_fault_class_is_required():
    errs = schema_validator.validate(dict(_BASE), "reconcile")
    assert errs, "fault_class should be required"


def test_each_valid_fault_class_passes():
    for fc in ("sub-actor", "specifier", "verifier"):
        rec = dict(_BASE, fault_class=fc)
        assert schema_validator.validate(rec, "reconcile") == [], fc


def test_unknown_fault_class_rejected():
    rec = dict(_BASE, fault_class="nonsense")
    assert schema_validator.validate(rec, "reconcile")


def test_schema_stays_closed():
    rec = dict(_BASE, fault_class="sub-actor", extra="nope")
    assert schema_validator.validate(rec, "reconcile")
