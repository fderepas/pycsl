"""Test 0831 — WL-04b regression lock (NEGATIVE twin of 0829/0830). # pycsl-expected: FAIL

Guards the WL-04b fix from becoming VACUOUS. The faithful `array <record>` element
model must prove the TRUE element field (0829/0830) WITHOUT admitting a FALSE
cross-field conflation.

Here `conflate_UNSOUND` returns `a[i].x` but claims `\result == a[i].y`; for a
`List[Point]` the record's `x` and `y` are DISTINCT, independent field labels, so this
is NOT provable (the pre-fix collapse read every element's fields through the SAME
opaque `get_<attr>` over a single collapsed int, which — combined with the ill-typed
collision — neither type-checked nor distinguished the fields). If this test ever
PASSES, the record element model has collapsed back to a single conflated value and
the WL-04b fix has regressed.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from dataclasses import dataclass
from typing import List


@dataclass
class Point:
    x: int
    y: int


#@ requires 0 <= i
#@ requires i < len(a)
#@ ensures \result == a[i].y
def conflate_UNSOUND(a: List[Point], i: int) -> int:
    """Returns field x but claims field y — false unless the fields are conflated."""
    return a[i].x


if __name__ == "__main__":
    # For a = [Point(1, 2)]: returns 1 (x), but the contract claims == a[0].y == 2. FALSE.
    assert conflate_UNSOUND([Point(1, 2)], 0) == 1
