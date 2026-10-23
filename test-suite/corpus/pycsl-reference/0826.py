"""Test 0826 — WL-04a regression lock (POSITIVE, List[str] LITERAL): a `List[str]`
built by a LIST LITERAL — assigned to a LOCAL or RETURNED directly — now realizes
its string ELEMENTS faithfully as `array string`, not a hashed-int collapse.

Before the fix, a list literal lowered every element through `_coerce_to_int`, so
`a = ["x", "y", "z"]` emitted `Array.make 3 (976090257)` (a `stable_hash`ed int
placeholder). A str-list LOCAL's element read `a[1]` was then wrong-typed (`int` vs
a `str` use site) and a `-> List[str]` RETURN mismatched its `array string` type —
ill-typed WhyML (Detector D2: TYPEERR), a legitimate function REJECTED. This is a
DISTINCT construction surface from the WL-04 PARAMETER element (0817). PyCSL now
builds the literal at the faithful element type — `array string` with the real
string values — so `a[i] : string` matches the use site and the true element
property is PROVABLE. The `-> List[str]` return's `\result[0]` reads natively
(`Array.get`), not the opaque `subscript_get`.

Ground truth: for `a = ["x", "y", "z"]`, `a[1]` is `"y"`; for `return ["a", "b"]`,
`\result[0]` is `"a"` and `\result[1]` is `"b"`; distinct cells are independent.
Twin: 0828 (# pycsl-expected: FAIL) asserts a FALSE element-content claim, which
must NOT be provable.
"""
_ = 0  # anchor
from typing import List


#@ ensures \result == "y"
def snd_str_local() -> str:
    """A str list LITERAL LOCAL's element is a STRING (was a hashed int -> TYPEERR)."""
    a = ["x", "y", "z"]
    return a[1]


#@ ensures \result[0] == "a"
#@ ensures \result[1] == "b"
def make_str_list() -> List[str]:
    """A `-> List[str]` return built by a literal is an `array string`, read natively."""
    return ["a", "b"]


if __name__ == "__main__":
    assert snd_str_local() == "y"
    r = make_str_list()
    assert r[0] == "a"
    assert r[1] == "b"
