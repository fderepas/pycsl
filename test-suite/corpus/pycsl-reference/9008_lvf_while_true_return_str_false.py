r"""Test 9008 -- lvF cap-return-exn-nonint (expected FAIL): false twin of 9006. The `absurd` that ends
a `while True:` block is reached only through the (false) loop exit, so it proves nothing about the
returned value: `\result == ""` is FALSE (CPython: drain("ab", 3) == "ab") and must not prove.
"""
# pycsl-expected: FAIL
from __future__ import annotations


#@ requires n >= 0
#@ ensures \result == ""
#@ assigns \nothing
def drain(s: str, n: int) -> str:
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while True:
        if i >= n:
            return s
        i = i + 1
