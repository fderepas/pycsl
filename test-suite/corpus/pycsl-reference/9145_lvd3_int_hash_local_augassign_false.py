r"""Test 9145 -- lvD3 (expected FAIL; proved under C2): `name += 1` after `name = "abc"` is an
implicit READ (CPython TypeError) even though the only explicit read is an f-string part; an AugAssign of
the local drops it from C2.
"""
# pycsl-expected: FAIL
from __future__ import annotations


#@ no_exception \all
#@ assigns \nothing
def f(x: int) -> str:
    name = x
    name = "abc"
    name += 1
    return f"*{name}"


if __name__ == "__main__":
    try:
        print("result", f(3))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
