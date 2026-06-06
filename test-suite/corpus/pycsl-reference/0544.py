"""Test 0544 — Negative: mutable default argument rejected (ownership R2).

`def f(x, acc=[])` binds a single mutable list shared across all calls — the
classic shared-alias bug, outside the value-semantics boundary
(`docs/pycsl-ownership-discipline.md` §2 R2). PyCSL rejects it at semantic
analysis with a clear diagnostic (crude ownership enforcement, §5), rather than
verifying it unsoundly. Companion negative test to 0284 (semantic error).
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import List


#@ ensures \result >= 0
#@ assigns \nothing
def f(x: int, acc: List[int] = []) -> int:
    return x
