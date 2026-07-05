"""Test 0816 — WL-03 regression lock (NEGATIVE twin of 0815). # pycsl-expected: FAIL

Guards the WL-03 fix from becoming VACUOUS. The faithful per-slot tuple model must
prove the TRUE slot content (0815) WITHOUT admitting a FALSE slot-content claim.
Here `ii_conflate` returns `t[0]` but claims `\result == t[1]`; for a homogeneous
`Tuple[int, int]` the two slots are INDEPENDENT record fields (`field0` vs `field1`),
so this is NOT provable (the pre-fix collapse conflated both slots into one opaque
int, which WOULD have made them equal). If this test ever PASSES again, the per-slot
model has collapsed back to a single opaque value and the WL-03 fix has regressed.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import Tuple


#@ ensures \result == t[1]
def ii_conflate_UNSOUND(t: Tuple[int, int]) -> int:
    """Returns slot 0 but claims slot 1 — false unless the slots are conflated."""
    return t[0]


if __name__ == "__main__":
    # For t = (3, 4): returns 3, but the contract claims == t[1] == 4. FALSE.
    assert ii_conflate_UNSOUND((3, 4)) == 3
