"""Regression net for the coordinator's loop-detection (exit-73 trigger).

Extracted from `coordinator.py` into `coordinator_loopdetect.py`; previously
untested. The coordinator halts human-needed when the same reconcile
recommendation recurs 3× in a row — this locks in the similarity + streak
semantics that decision depends on.
"""
import sys
from pathlib import Path

_AGENTS = Path(__file__).resolve().parents[2] / "src" / "pycsl" / "agents"
sys.path.insert(0, str(_AGENTS))

import coordinator_loopdetect as ld  # noqa: E402


def _rec(target, text):
    return {"target": target, "recommendation": text}


def test_are_similar_normalises_case_and_whitespace():
    assert ld.are_similar(_rec("F.py", " Add invariant "), _rec("f.py", "add invariant"))
    assert not ld.are_similar(_rec("f.py", "add invariant"), _rec("g.py", "add invariant"))
    assert not ld.are_similar(_rec("f.py", "add invariant"), _rec("f.py", "weaken ensures"))


def test_consecutive_similar_counts_only_the_tail_streak():
    r = _rec("f.py", "add invariant")
    other = _rec("f.py", "weaken ensures")
    # tail = [other, r, r]  →  streak of 2 similar to r
    assert ld.consecutive_similar(r, [other, r, r]) == 2
    # a non-similar tail entry breaks the streak
    assert ld.consecutive_similar(r, [r, r, other]) == 0
    assert ld.consecutive_similar(r, []) == 0


def test_three_in_a_row_is_the_halt_threshold():
    r = _rec("f.py", "add invariant")
    # the coordinator halts (exit 73) when this reaches 3
    assert ld.consecutive_similar(r, [r, r]) == 2          # 3rd occurrence → 3
    assert ld.consecutive_similar(r, [r, r, r]) == 3
