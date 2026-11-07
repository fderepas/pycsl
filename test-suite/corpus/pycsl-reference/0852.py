"""Test 0852 — WL-04g NEGATIVE lock (int+float mixed literal). # pycsl-expected: FAIL

A mixed `[1, 2.5]` literal has no faithful `array τ` element type: the int-coercion default
left the float `2.5` in an `array int` (silent Why3 TYPEERR / broken emission). WL-04g makes
it FAIL CLOSED — PyCSL REJECTS the heterogeneous literal with a clear diagnostic. The false
content claim `a[1] == 2` (the int-truncated value) must NEVER prove; the literal is rejected
before any coercion. If this reports Verification SUCCESS, the boundary has regressed.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import List


#@ ensures \result == 2
def mixed_int_float_rejected() -> int:
    a = [1, 2.5]
    return a[1]
