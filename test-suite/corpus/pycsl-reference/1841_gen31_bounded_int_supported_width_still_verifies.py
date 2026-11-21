r"""Test 1841 — gen #31 CONTROL for 1840 (expected PASS): a SUPPORTED width is untouched.

`bounded_int(32)` is one of the five widths Why3's `mach.int` actually provides, and the
identical program verifies. Without this file the refusal in 1840 would be indistinguishable
from a ban on `bounded_int`.

The corpus already uses 32 and 64 (0202/0203/0204); this file pins that the width REFUSAL
does not reach them.
"""
# pycsl-expected: PASS
_ = 0  # anchor


#@ assumes bounded_int(32)
#@ requires 0 <= x and x <= 100
#@ ensures \result >= 0
def f(x: int) -> int:
    return x + 20
