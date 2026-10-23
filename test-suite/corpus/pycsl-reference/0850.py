"""Test 0850 — WL-04g POSITIVE lock: a HOMOGENEOUS list literal is UNAFFECTED by the
mixed-element reject guard.

The WL-04g fail-closed guard (wrong-lowering-to-fix.md §WL-04 mixed residual) rejects
a HETEROGENEOUS list literal (`[1, "x"]`, `[1, 2.5]`, `[1, Point(2,3)]`) — no faithful
`array τ` element type. This lock guards against OVER-rejection: a homogeneous all-int
literal still builds `array int` and proves its faithful element content. If this test
ever FAILs, the guard has become too broad and is rejecting sound homogeneous literals.
"""
_ = 0  # anchor
from typing import List


#@ ensures \result == 20
def homogeneous_int_ok() -> int:
    """[10, 20, 30] is homogeneous — array int, element 1 is 20."""
    a = [10, 20, 30]
    return a[1]


if __name__ == "__main__":
    assert homogeneous_int_ok() == 20
