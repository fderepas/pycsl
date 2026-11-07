"""Test 0828 — WL-04a regression lock (NEGATIVE twin of 0826/0827). # pycsl-expected: FAIL

Guards the WL-04a list-literal fix from becoming VACUOUS. The faithful `array string`
literal construction must prove the TRUE element content (0826/0827) WITHOUT admitting
a FALSE element-content claim.

Here `conflate_UNSOUND` builds `["x", "y", "z"]` and returns `a[0]` but claims
`\result == "y"` (element 1); for a faithfully-constructed `array string` the elements
at distinct indices are INDEPENDENT cells, so this is NOT provable. If this test ever
PASSES, the literal element model has collapsed back to a single opaque value (the
pre-fix hashed-int placeholder read through the SAME `subscript_get`) and the WL-04a
fix has regressed.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import List


#@ ensures \result == "y"
def conflate_UNSOUND() -> str:
    """Builds ["x","y","z"], returns element 0 but claims == "y" (element 1) — FALSE."""
    a = ["x", "y", "z"]
    return a[0]


if __name__ == "__main__":
    # Returns "x", but the contract claims == "y". FALSE unless cells are conflated.
    assert conflate_UNSOUND() == "x"
