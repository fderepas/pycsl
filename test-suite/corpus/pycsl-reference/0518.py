"""Test 0518 — float (negative): a false real-arithmetic contract fails (no-more-int Stage D).

Under real semantics `x + x` is `2x`, not `3x`, so `ensures \result == x + x + x` is unprovable
for the body `return x + x`. Confirms float arithmetic is genuinely over the reals (not the old
unsound int collapse). Expected-FAIL = the postcondition does not discharge."""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == x + x + x
#@ assigns \nothing
def double(x: float) -> float:
    return x + x
