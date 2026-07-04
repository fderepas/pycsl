"""Test 0769 — projection list comprehension is content-faithful.

cleared-array.md S2. `[p.x for p in a]` over a `List[Point]` now lowers to a
per-instance `list_content_comp_<n>` val whose `ensures` gives
`length result = length a` and `forall i. result[i] = get_x(a[i])` — the SAME
deterministic getter a driver's own `\result[k] == a[k].x` lowers to. So a driver
can prove the result is the element-wise field projection of the source, which
the old opaque `list_comp` could not express.

Enabling pieces: the contract grammar now parses `a[k].field` (subscript-then-
projection); the abstract getter `get_x` is emitted as a pure `val function` in
spec context so it is usable in the `ensures` and denotes one value across both
mentions. No global axiom — the content law is a definitional `ensures` on the
abstract val, discharged at the use site.
"""
_ = 0  # anchor
from dataclasses import dataclass
from typing import List


@dataclass
class Point:
    x: int
    y: int


#@ ensures \forall k; 0 <= k and k < \length(\result) ==> \result[k] == a[k].x
#@ ensures \length(\result) == \length(a)
#@ assigns \nothing
def project_x(a: List[Point]) -> List[int]:
    return [p.x for p in a]
