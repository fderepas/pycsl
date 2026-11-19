"""Test 0840 — WL-04c regression lock (NEGATIVE twin of 0839). # pycsl-expected: FAIL

Guards the WL-04c fix from becoming VACUOUS. The faithful `array <record>` literal
model must prove the TRUE element field (0839) WITHOUT admitting a FALSE cross-field
conflation.

Here `conflate_UNSOUND` builds `a = [Point(1, 5)]` and returns `a[0].x` (== 1) but
claims `\result == 5`; for the record literal `Point(1, 5)` the fields `x` and `y`
are DISTINCT independent labels, so the 5 (which is `a[0].y`) is NOT the returned
`a[0].x`. If this test ever PASSES, the literal element model has collapsed the two
fields into one conflated value and the WL-04c fix has regressed.

(A single-element literal keeps the false goal fast: the concrete `array <record>`
construction makes a multi-element FALSE goal grind the SMT solver, while the true
laws in 0839 discharge instantly.)
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import NamedTuple, List


class Point(NamedTuple):
    x: int
    y: int


#@ ensures \result == 5
def conflate_UNSOUND() -> int:
    """Returns field x (== 1) but claims == 5 (field y) — false unless conflated."""
    a = [Point(1, 5)]
    return a[0].x


if __name__ == "__main__":
    # a[0].x == 1, but the contract claims == a[0].y == 5. FALSE.
    assert conflate_UNSOUND() == 1
