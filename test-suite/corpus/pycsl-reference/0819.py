"""Test 0819 — WL-04 regression lock (NEGATIVE twin of 0817/0818). # pycsl-expected: FAIL

Guards the WL-04 fix from becoming VACUOUS. The faithful `array string`/`array real`
element model must prove the TRUE element content (0817/0818) WITHOUT admitting a
FALSE element-content claim.

Here `conflate_UNSOUND` returns `a[0]` but claims `\result == a[1]`; for a `List[str]`
the elements at distinct indices are INDEPENDENT array cells, so this is NOT provable
(the pre-fix collapse read every element through the SAME opaque `subscript_get`
int, which — combined with the ill-typed collision — would neither type-check nor
distinguish the cells). If this test ever PASSES, the element model has collapsed
back to a single opaque value and the WL-04 fix has regressed.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import List


#@ requires len(a) >= 2
#@ ensures \result == a[1]
def conflate_UNSOUND(a: List[str]) -> str:
    """Returns element 0 but claims element 1 — false unless the cells are conflated."""
    return a[0]


if __name__ == "__main__":
    # For a = ["x", "y"]: returns "x", but the contract claims == a[1] == "y". FALSE.
    assert conflate_UNSOUND(["x", "y"]) == "x"
