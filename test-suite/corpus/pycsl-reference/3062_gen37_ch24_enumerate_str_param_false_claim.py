r"""Test 3062 — gen #37 ch24 (expected FAIL): FALSE twin of 3060's `last_decl`. With no
matching line (e.g. `[]`) the result is -1 (CPython: -1), so `\result >= 0` is false; it
must stay UNPROVED now that the `enumerate(<List[str] param>)` loop type-checks
(non-vacuity of the seam).
"""
# pycsl-expected: FAIL
from typing import List


#@ ensures \result >= 0
#@ assigns \nothing
def last_decl(xs: List[str], tag: str) -> int:
    r = -1
    #@ loop invariant -1 <= r and r < \length(xs)
    for i, line in enumerate(xs):
        if line.startswith((tag, "val ")):
            r = i
    return r


if __name__ == "__main__":
    print(last_decl([], "type "))
