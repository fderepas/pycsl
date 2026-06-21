"""Regression tests for the best-of-N prover-result merge (soundness-issue.md).

The bug (commit fa3668d): `_merge_best_of_n` keyed goals by their header alone,
but `why3 -a split_vc` emits DISTINCT sub-goals with a byte-identical header (the
then/else branch obligations of one postcondition share a source line and label).
A Valid sibling then MASKED a non-Valid one, producing a false `Verification
SUCCESS`. These tests pin the contract that broke and the Tier-0 fail-closed
conservation backstop.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Make src/pycsl importable (same convention as tests/test_audit_proof.py).
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src" / "pycsl"))

from pycsl import (  # noqa: E402
    _merge_best_of_n,
    _parse_goal_blocks,
    _check_goal_conservation,
    _MergeConservationError,
)


# --- helpers ---------------------------------------------------------------

def _block(line: int, verdict: str, label: str = "Postcondition of goal f'vc") -> str:
    """One why3 goal block: a 2-line header (File + Sub-goal) then a result line."""
    return (
        f'File "f.mlw", line {line}, characters 4-9:\n'
        f"Sub-goal {label}.\n"
        f"Prover result is: {verdict}"
    )


def _output(*blocks: str) -> str:
    """Join goal blocks the way `why3 prove` emits them: separated by a blank line.
    With that separator, every block after the first carries a leading blank into
    its header (matching `_parse_goal_blocks`), which is precisely why two ADJACENT
    same-line sub-goals end up with byte-identical headers."""
    return "\n\n".join(blocks)


# --- _parse_goal_blocks: same-line siblings are DISTINCT blocks -------------

def test_parse_keeps_colliding_headers_as_separate_blocks() -> None:
    """Two ADJACENT sub-goals at the same line+label are two blocks with a
    byte-identical header — the exact collision that masked the false-green."""
    out = _output(
        _block(10, "Valid (0.01s, 1 steps)", label="Precondition of goal f'vc"),
        _block(119, "Timeout (30.00s, 1 steps)"),
        _block(119, "Valid (0.01s, 1 steps)"),
    )
    blocks = _parse_goal_blocks(out)
    assert len(blocks) == 3
    # the two line-119 postcondition blocks have IDENTICAL headers
    h119 = [h for h, _ in blocks if "line 119" in h]
    assert len(h119) == 2 and h119[0] == h119[1]


# --- _merge_best_of_n: a Valid sibling must NOT mask a non-Valid one --------

def test_merge_does_not_mask_timeout_sibling_at_same_header() -> None:
    """THE regression: then-branch Timeout + else-branch Valid at the same header.
    The merged output must still contain the Timeout (so downstream FAILS)."""
    single_prover_output = _output(
        _block(10, "Valid (0.01s, 1 steps)", label="Precondition of goal f'vc"),
        _block(119, "Timeout (30.00s, 25638167 steps)"),  # then-branch (live, unproven)
        _block(119, "Valid (0.01s, 762 steps)"),          # else-branch (dead)
    )
    merged = _merge_best_of_n([single_prover_output])
    blocks = _parse_goal_blocks(merged)
    assert len(blocks) == 3, "merge collapsed two same-header sub-goals into one"
    verdicts = [rl for _, rl in blocks]
    assert any("Timeout" in v for v in verdicts), "Timeout sibling was masked — false green"


def test_merge_best_of_n_promotes_per_occurrence_across_provers() -> None:
    """Legitimate best-of-N: occurrence k in prover A pairs with occurrence k in B.
    A's [Timeout, Valid] and B's [Valid, Timeout] (same two headers) merge to
    [Valid, Valid] — each sub-goal proven by SOME prover."""
    lead = _block(10, "Valid (1s, 0 steps)", label="Precondition of goal f'vc")
    a = _output(lead, _block(119, "Timeout (1s, 1 steps)"), _block(119, "Valid (1s, 2 steps)"))
    b = _output(lead, _block(119, "Valid (1s, 3 steps)"), _block(119, "Timeout (1s, 4 steps)"))
    merged = _merge_best_of_n([a, b])
    blocks = _parse_goal_blocks(merged)
    v119 = [rl for h, rl in blocks if "line 119" in h]
    assert len(v119) == 2
    assert all("Valid" in v for v in v119), "per-occurrence best-of-N failed"


def test_merge_unique_headers_unaffected() -> None:
    """No collision => behaviour is unchanged (occurrence index always 0)."""
    out = _output(_block(10, "Valid (1s, 1 steps)"), _block(20, "Timeout (1s, 1 steps)"))
    merged = _merge_best_of_n([out])
    blocks = _parse_goal_blocks(merged)
    assert len(blocks) == 2
    assert any("Timeout" in rl for _, rl in blocks)


# --- _check_goal_conservation: trust-free fail-closed backstop --------------

def test_conservation_passes_when_counts_match() -> None:
    first = _output(
        _block(10, "Valid (1s, 0 steps)", label="Precondition of goal f'vc"),
        _block(119, "Timeout (1s, 1 steps)"),
        _block(119, "Valid (1s, 2 steps)"),
    )
    merged = _merge_best_of_n([first])  # correct merge preserves all three
    _check_goal_conservation(first, merged)  # must not raise


def test_conservation_raises_when_a_goal_is_dropped() -> None:
    """Simulate a future regression of the merge that drops a goal: the backstop
    must refuse to report a verdict, independent of the merge implementation."""
    first = _output(
        _block(10, "Valid (1s, 0 steps)", label="Precondition of goal f'vc"),
        _block(119, "Timeout (1s, 1 steps)"),
        _block(119, "Valid (1s, 2 steps)"),
    )
    lossy_merged = _output(  # the Timeout sibling was dropped (header-keyed collapse)
        _block(10, "Valid (1s, 0 steps)", label="Precondition of goal f'vc"),
        _block(119, "Valid (1s, 2 steps)"),
    )
    with pytest.raises(_MergeConservationError):
        _check_goal_conservation(first, lossy_merged)


def test_conservation_allows_zero_goals() -> None:
    _check_goal_conservation("", "")  # no goals to prove — must not raise
