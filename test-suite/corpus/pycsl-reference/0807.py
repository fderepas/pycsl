"""Test 0807 — BOUNDARY: nesting deeper than the depth cap stays opaque/rejected.

nested-list.md §8/§9 EXTENSION depth-cap boundary. The type recursion
(`_M5_MAX_NEST_DEPTH = 4`) faithfully models nesting up to depth 4
(`List[List[List[List[int]]]]` ~ `array (seq (seq (seq int)))`; drivers 0805
depth-3, and depth-4 proven in the Gate-B spike `nested-list-deep.mlw`). A
FIFTH level is BEYOND the cap: the element type recursion returns None, the
param is NOT a nested-elem list, and the deep read `a[i][j][k][l][m]` lowers to
the opaque `subscript_get` fallback — which does NOT type-check as a faithful
nested read, so a content claim over it is REJECTED, never silently accepted as
a faithful nested value. This pins the honest cap (expected FAIL: not verified).
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import List


#@ ensures \result == a[i][j][k][l][m]
def too_deep(a: List[List[List[List[List[int]]]]],
             i: int, j: int, k: int, l: int, m: int) -> int:
    return a[i][j][k][l][m]
