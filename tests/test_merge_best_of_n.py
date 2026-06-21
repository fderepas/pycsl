"""Regression tests for the best-of-N prover-result merge (soundness-issue.md).

The bug (commit fa3668d): `_merge_best_of_n` keyed goals by their header alone,
but `why3 -a split_vc` emits DISTINCT sub-goals with a byte-identical header (the
then/else branch obligations of one postcondition share a source line and label).
A Valid sibling then MASKED a non-Valid one, producing a false `Verification
SUCCESS`. These tests pin the contract that broke and the Tier-0 fail-closed
conservation backstop.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Make src/pycsl importable (same convention as tests/test_audit_proof.py).
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src" / "pycsl"))

from pycsl import (  # noqa: E402
    _parse_goal_blocks,
    _check_goal_conservation,
    _MergeConservationError,
    _parse_why3_json,
    _json_goal_records,
    _merge_records_best_of_n,
    _synthesize_legacy_text,
    _residual_selectors_from_records,
    _record_is_valid,
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


# --- _check_goal_conservation: trust-free fail-closed backstop --------------

def test_conservation_passes_when_counts_match() -> None:
    first = _output(
        _block(10, "Valid (1s, 0 steps)", label="Precondition of goal f'vc"),
        _block(119, "Timeout (1s, 1 steps)"),
        _block(119, "Valid (1s, 2 steps)"),
    )
    _check_goal_conservation(first, first)  # same goal count => must not raise


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


# ===========================================================================
# #6: structured `why3 prove --json` path (records, not text re-grepping)
# ===========================================================================

def _rec(line, answer, name="f'vc", expl=("postcondition",), sc=14, ec=24,
         fname="x.mlw", t=0.0, step=0):
    """A why3 --json goal record, matching the observed 1.8.2 shape."""
    return {
        "prover-result": {"answer": answer, "time": t, "step": step, "ce-models": []},
        "term": {"explanations": list(expl), "goal_name": name,
                 "loc": {"file-name": fname, "start-line": line, "end-line": line,
                         "start-char": sc, "end-char": ec}},
    }


def _json_stream(*recs) -> str:
    """why3 emits a STREAM of concatenated objects (not an array)."""
    return "\n".join(json.dumps(r) for r in recs)


def test_parse_why3_json_handles_concatenated_stream() -> None:
    out = _json_stream(_rec(119, "Timeout"), _rec(119, "Valid"))
    recs = _json_goal_records(out)
    assert len(recs) == 2
    assert [_record_is_valid(r) for r in recs] == [False, True]


def test_parse_why3_json_handles_single_array() -> None:
    out = json.dumps([_rec(10, "Valid"), _rec(20, "Valid")])
    assert len(_json_goal_records(out)) == 2


def test_parse_why3_json_ignores_non_goal_objects() -> None:
    out = _json_stream({"some": "metadata"}, _rec(10, "Valid"))
    assert len(_json_goal_records(out)) == 1


def test_record_merge_does_not_mask_timeout_sibling() -> None:
    """THE #6 regression: two byte-identical records (same loc/name/expl) — the
    then/else branch collision — must stay distinct; a Valid one must NOT mask the
    Timeout one."""
    recs = [_rec(119, "Timeout"), _rec(119, "Valid")]  # identical _record_key
    merged = _merge_records_best_of_n([recs])
    assert len(merged) == 2, "collapsed two same-key records into one"
    assert not all(_record_is_valid(r) for r in merged), "Timeout sibling was masked"


def test_record_merge_best_of_n_by_occurrence_across_provers() -> None:
    """A's [Timeout, Valid] and B's [Valid, Timeout] (same key) merge per occurrence
    to [Valid, Valid]."""
    a = [_rec(119, "Timeout"), _rec(119, "Valid")]
    b = [_rec(119, "Valid"), _rec(119, "Timeout")]
    merged = _merge_records_best_of_n([a, b])
    assert len(merged) == 2
    assert all(_record_is_valid(r) for r in merged), "per-occurrence best-of-N failed"


def test_record_only_literal_valid_counts() -> None:
    for ans in ("Invalid", "Unknown", "Timeout", "OutOfMemory", "Failure"):
        assert not _record_is_valid(_rec(1, ans))
    assert _record_is_valid(_rec(1, "Valid"))


def test_synthesize_round_trips_one_block_per_record() -> None:
    """Synthesised text has exactly one goal block per record, and the tokens are
    grep-compatible: Valid -> 'Valid (', non-Valid -> Invalid/Timeout/Unknown."""
    recs = [_rec(10, "Valid"), _rec(119, "Timeout"), _rec(119, "Valid"),
            _rec(200, "OutOfMemory")]
    text = _synthesize_legacy_text(recs)
    blocks = _parse_goal_blocks(text)
    assert len(blocks) == 4
    results = [rl for _, rl in blocks]
    assert sum("Valid (" in rl for rl in results) == 2
    assert any("Timeout" in rl for rl in results)
    assert any("Unknown" in rl for rl in results)  # OutOfMemory -> leading Unknown


def test_residual_selectors_from_records() -> None:
    recs = [_rec(10, "Valid", fname="a.mlw"), _rec(119, "Timeout", fname="a.mlw"),
            _rec(119, "Valid", fname="a.mlw")]
    assert _residual_selectors_from_records(recs) == ["a.mlw:119"]
    # all valid -> no residuals
    assert _residual_selectors_from_records([_rec(10, "Valid")]) == []
    # missing loc -> None (caller falls back to full-file re-run)
    bad = {"prover-result": {"answer": "Timeout"}, "term": {"goal_name": "g'vc"}}
    assert _residual_selectors_from_records([bad]) is None
