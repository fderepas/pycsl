"""Test 0805 — DEEPER nested read a[i][j][k] is content-faithful (depth 3).

nested-list.md §8/§9 EXTENSION (deeper nesting). A `List[List[List[int]]]` param
lowers to `array (seq (seq int))` (outer `array`, pure inner `seq (seq int)`), so
the subscript lowering composes `Seq.get` to depth 3:
    a[i][j][k]  ~  Seq.get (Seq.get (a[i]) j) k
NOT the opaque `int` collapse and NOT capped at 2 levels. The subscript-lowering
is now recursive (peel one container level per index level, up to the type
recursion depth bound 4), so a driver can prove the three-index content
`\result == a[i][j][k]`. No new axiom (the Seq read law is Why3 stdlib).
"""
_ = 0  # anchor
from typing import List

#@ requires 0 <= i and i < len(a)
#@ requires 0 <= j and j < len(a[i])
#@ requires 0 <= k and k < len(a[i][j])
#@ ensures \result == a[i][j][k]
def deep_read(a: List[List[List[int]]], i: int, j: int, k: int) -> int:
    return a[i][j][k]

if __name__ == "__main__":
    assert deep_read([[[1, 2], [3]], [[4, 5, 6]]], 1, 0, 2) == 6
