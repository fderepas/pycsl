r"""Test 1312 — ROUTE #114 negative: the tuple key `(y, 1)` was replaced by a hash of its TEXT `(!y, 1)`, the same integer before and after y changed, so `(y, 1) in d` PROVED true (CPython False). A genuine tuple in an int position is now Why3 `(any int)` — unknown, never a text hash.
"""
# pycsl-expected: FAIL
from typing import Dict, Tuple

#@ ensures \result == 1
#@ assigns \nothing
def f(x: int) -> int:
    y = x
    d: Dict[Tuple[int, int], int] = {}
    d[(y, 1)] = 5
    y = y + 1
    if (y, 1) in d:
        return 1
    return 0
