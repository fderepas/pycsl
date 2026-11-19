"""Test 0844 — WL-04e regression lock (NEGATIVE twin of 0843). # pycsl-expected: FAIL

Guards the WL-04e fix from becoming VACUOUS. The faithful `array point` element model
(plain positional-`__init__` class) must prove the TRUE element field (0843) WITHOUT
admitting a FALSE cross-element conflation.

Here `conflate_UNSOUND` over a flat `List[Point]` returns `a[0].x` but claims
`\result == a[1].x`; distinct array slots hold INDEPENDENT records, so the two elements'
`x` fields are NOT equal in general. If this test ever PASSES, the element model has
collapsed every element into one conflated value (the pre-fix `array int` failure mode)
and the WL-04e fix has regressed.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import List


class Point:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y


#@ requires len(a) > 1
#@ ensures \result == a[1].x
def conflate_UNSOUND(a: List[Point]) -> int:
    """Returns a[0].x but claims == a[1].x — false unless the elements are conflated."""
    return a[0].x


if __name__ == "__main__":
    # a[0].x == 3, but the contract claims == a[1].x == 7. FALSE.
    pts = [Point(3, 4), Point(7, 8)]
    assert conflate_UNSOUND(pts) == 3
