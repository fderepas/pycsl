r"""Test 9007 -- lvF cap-return-exn-nonint (expected FAIL): false twin of 9005. The in-loop return
carries "x" through `Return_str`; when `n <= 3` the loop exits normally and the tail returns `s`, so
`\result == "x"` is FALSE of the program (CPython: first_hit("ab", 2) == "ab") and must not prove.
"""
# pycsl-expected: FAIL
from __future__ import annotations


#@ requires n >= 0
#@ ensures \result == "x"
#@ assigns \nothing
def first_hit(s: str, n: int) -> str:
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        if i == 3:
            return "x"
        i = i + 1
    return s
