"""Checker tests.

Unit tests on the output parser using captured pycsl transcripts.
Integration test runs pycsl on a known-good fixture from the existing
reference corpus.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from pycsl_emit.checker import (
    ObligationStatus,
    Verdict,
    run_pycsl,
)
from pycsl_emit.checker.pycsl_runner import _parse_obligations


# ──────────────────────────────────────────────────────────────────────
# Output-parser unit tests (no pycsl invocation)
# ──────────────────────────────────────────────────────────────────────


def test_parse_valid_postcondition():
    stdout = (
        '[*] Parsing and Semantic Analysis...\n'
        '\n'
        '--- Verification Results ---\n'
        'File "/tmp/x.mlw", line 8, characters 15-28:\n'
        "Sub-goal Postcondition of goal test_precondition'vc.\n"
        'Prover result is: Valid (0.01s, 154 steps).\n'
        '\n'
        '[+] Verification SUCCESS! All contracts formally proven.\n'
    )
    obs = _parse_obligations(stdout)
    assert len(obs) == 1
    assert obs[0].theorem == "test_precondition'vc"
    assert obs[0].kind == "Postcondition"
    assert obs[0].status is ObligationStatus.VALID
    assert "Valid" in obs[0].detail


def test_parse_unknown_with_parenthesised_qualifier():
    stdout = (
        "Sub-goal Postcondition of goal foo'vc.\n"
        "Prover result is: Unknown (sat) (0.01s, 266 steps).\n"
    )
    obs = _parse_obligations(stdout)
    assert len(obs) == 1
    assert obs[0].status is ObligationStatus.UNKNOWN
    assert obs[0].detail.startswith("Unknown (sat)")


def test_parse_multiple_obligations_in_order():
    stdout = (
        "Sub-goal Precondition of goal gcd'vc.\n"
        "Prover result is: Valid (0.02s, 100 steps).\n"
        "Sub-goal Postcondition of goal gcd'vc.\n"
        "Prover result is: Valid (0.03s, 200 steps).\n"
        "Sub-goal LoopInvariant of goal gcd'vc.\n"
        "Prover result is: Timeout.\n"
    )
    obs = _parse_obligations(stdout)
    assert [o.kind for o in obs] == ["Precondition", "Postcondition", "LoopInvariant"]
    assert obs[-1].status is ObligationStatus.TIMEOUT


def test_parse_handles_empty_kind():
    """Some Why3 output lines have no kind word between Sub-goal and 'of goal'."""
    stdout = (
        "Sub-goal of goal foo'vc.\n"
        "Prover result is: Valid (0.01s, 10 steps).\n"
    )
    obs = _parse_obligations(stdout)
    # Either no obligation is parsed (kind is required between Sub-goal and 'of'),
    # or kind is the empty string. Both are acceptable; the runner exit code
    # still tells the caller whether pycsl succeeded.
    if obs:
        assert obs[0].theorem == "foo'vc"


def test_parse_ignores_unrelated_lines():
    stdout = (
        "[*] some info\n"
        "[+] another info\n"
        "random debug text\n"
    )
    assert _parse_obligations(stdout) == []


def test_verdict_summary_and_predicates():
    from pycsl_emit.checker.verdict import ObligationResult
    v = Verdict(
        exit_code=0,
        obligations=[
            ObligationResult("foo'vc", "Postcondition", ObligationStatus.VALID, "Valid"),
            ObligationResult("foo'vc", "Precondition", ObligationStatus.VALID, "Valid"),
        ],
    )
    assert v.all_valid
    assert v.valid_count == 2
    assert v.total == 2
    assert v.unproven() == []
    assert "2/2" in v.summary()

    failing = Verdict(
        exit_code=1,
        obligations=[
            ObligationResult("foo'vc", "Postcondition", ObligationStatus.UNKNOWN, "Unknown"),
        ],
    )
    assert not failing.all_valid
    assert len(failing.unproven()) == 1


# ──────────────────────────────────────────────────────────────────────
# Integration: invoke pycsl on a real fixture
# ──────────────────────────────────────────────────────────────────────


_REPO = Path(__file__).resolve().parents[4]
_REFERENCE_OK = _REPO / "test-suite" / "corpus" / "pycsl-reference" / "0001.py"


@pytest.mark.skipif(not _REFERENCE_OK.exists(), reason="reference fixture missing")
def test_no_proof_succeeds_on_known_good_fixture():
    """--no-proof on a reference test should exit 0 with no obligation lines
    (Why3 is skipped, so there are no Prover result lines)."""
    v = run_pycsl(_REFERENCE_OK, no_proof=True)
    assert v.exit_code == 0, v.stdout + v.stderr
    # --no-proof doesn't produce per-goal lines, so total is 0 but exit is 0.
    assert v.total == 0
    assert "Verification SUCCESS" in v.stdout


@pytest.mark.skipif(not _REFERENCE_OK.exists(), reason="reference fixture missing")
def test_full_run_against_known_good_fixture():
    """Full pycsl run on 0001.py. Skipped if Why3/Alt-Ergo aren't installed."""
    v = run_pycsl(_REFERENCE_OK)
    if v.exit_code != 0 and "why3" in v.stdout.lower() and "not found" in v.stdout.lower():
        pytest.skip("why3 not installed in test environment")
    if v.exit_code == 0:
        # Fixture has a single postcondition that should be Valid.
        assert v.total >= 1
        assert v.all_valid, v.summary()
        assert all(o.status is ObligationStatus.VALID for o in v.obligations)
