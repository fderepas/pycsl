"""Test 0818 — WL-04 regression lock (POSITIVE, List[float]): a FLAT `List[float]`
PARAMETER now realizes its element as the faithful `real` type, so an element read
`a[i]` reads a `float` — not the opaque `int` collapse.

Before the fix, a `List[float]`-annotated PARAMETER lowered to `array int` while the
use site was faithfully typed (`float` return), producing INTERNALLY-INCONSISTENT,
ill-typed WhyML (`let f (a: array int) ... : real = a[i]`, `a[i] : int` vs return
`: real`) — Detector D2: TYPEERR. PyCSL now realizes a flat `List[float]` param as
`array real`, so `a[i] : real` matches the `float` return and the faithful element
read `\result == a[i]` is PROVABLE — the fractional element value is preserved, never
truncated to int.

Ground truth: for a list `a` of floats, `a[i]` is the i-th element, a `float`. Twin:
0819 (# pycsl-expected: FAIL) also covers the false element-content claim for the str
list; here the float value is preserved exactly.
"""
_ = 0  # anchor
from typing import List


#@ requires 0 <= i
#@ requires i < len(a)
#@ ensures \result == a[i]
def get_float(a: List[float], i: int) -> float:
    """A flat `List[float]` param's element is a REAL (was an opaque int -> TYPEERR)."""
    return a[i]


#@ requires len(a) >= 1
#@ ensures \result == a[0]
def head_float(a: List[float]) -> float:
    """The head element is a `float`; its fractional value is preserved (not int)."""
    return a[0]


if __name__ == "__main__":
    assert get_float([1.5, 2.5, 3.5], 1) == 2.5
    assert head_float([0.25, 9.0]) == 0.25
