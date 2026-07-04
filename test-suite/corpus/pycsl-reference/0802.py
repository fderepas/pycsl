"""Test 0802 — in-place inner ELEMENT mutation a[i][j]=v reads back (POSITIVE).

nested-list-mutable.md. A `List[List[int]]` param that is IN-PLACE INNER-MUTATED
(`a[i][j] = v` in the body) can NOT use the read-only `array (seq int)` model —
the inner `seq` is a PURE/immutable Why3 value. A usage/mutation analysis
(Module5 `_collect_inner_mutated_params`) instead routes such a param to the
MUTABLE built-in `matrix int` model: `a[i][j]=v` lowers to `Matrix.set a i j v`,
the read `a[i][j]` to `Matrix.get a i j`, `len(a)` to `a.rows`, `len(a[i])` to
`a.columns` (rectangular). So a driver can prove the mutation reads back:
`(a[i][j] = v; a[i][j]) == v`. The Gate-B spike (spikes/nested-list-mutable.mlw)
proved this Valid in BOTH Alt-Ergo and Z3. No new axiom (Matrix get/set laws are
Why3 stdlib).

Read-only nested lists stay on `array (seq int)` (ragged-capable — 0797/0798);
non-int-leaf / append / ragged in-place mutation stay rejected (0804).
"""
_ = 0  # anchor
from typing import List

#@ requires 0 <= i and i < len(a)
#@ requires 0 <= j and j < len(a[i])
#@ ensures \result == v
def inner_mutate(a: List[List[int]], i: int, j: int, v: int) -> int:
    a[i][j] = v
    return a[i][j]

if __name__ == "__main__":
    m = [[1, 2, 3], [4, 5, 6]]
    assert inner_mutate(m, 1, 2, 99) == 99
    assert m[1][2] == 99
