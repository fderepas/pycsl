"""Test 0798 — inner length len(a[i]) is a real per-row quantity.

nested-list.md S5. Over `array (seq int)`, `len(a[i])` is `Seq.length (a[i])` —
a faithful per-row length. The old `matrix int` model (rectangular, single
`columns`) could not express a ragged per-row length at all; the `int`-collapse
lost the inner list entirely. No new axiom.
"""
_ = 0  # anchor
from typing import List

#@ requires 0 <= i and i < len(a)
#@ ensures \result == len(a[i])
def inner_len(a: List[List[int]], i: int) -> int:
    return len(a[i])

if __name__ == "__main__":
    assert inner_len([[1, 2], [3, 4, 5]], 1) == 3
