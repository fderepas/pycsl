"""Test 0817 — WL-04 regression lock (POSITIVE, List[str]): a FLAT `List[str]`
PARAMETER now realizes its element as the faithful `string` type, so an element
read `a[i]` reads a `str` — not the opaque `int` collapse.

Before the fix, a `List[str]`-annotated PARAMETER lowered to `array int` while the
use site was faithfully typed (`str` return), producing INTERNALLY-INCONSISTENT,
ill-typed WhyML (`let f (a: array int) ... : string = a[i]`, `a[i] : int` vs return
`: string`) — Detector D2: TYPEERR, a legitimate function REJECTED. PyCSL now
realizes a flat `List[str]` param as `array string` (the one-level-up analog of the
nested-list `array (seq τ)` model), so `a[i] : string` matches the `str` return and
the faithful element read `\result == a[i]` is PROVABLE.

Ground truth: for a list `a` of strings, `a[i]` is the i-th element, a `str`; the
elements are independent. Twin: 0819 (# pycsl-expected: FAIL) asserts a FALSE
element-content claim (a str-list read equals a wrong element), which must NOT be
provable.
"""
_ = 0  # anchor
from typing import List


#@ requires 0 <= i
#@ requires i < len(a)
#@ ensures \result == a[i]
def get_str(a: List[str], i: int) -> str:
    """A flat `List[str]` param's element is a STRING (was an opaque int -> TYPEERR)."""
    return a[i]


#@ requires len(a) >= 2
#@ ensures \result == a[1]
def snd_str(a: List[str]) -> str:
    """A concrete index reads the SECOND string element, independent of the first."""
    return a[1]


if __name__ == "__main__":
    assert get_str(["a", "b", "c"], 2) == "c"
    assert snd_str(["hi", "bye"]) == "bye"
