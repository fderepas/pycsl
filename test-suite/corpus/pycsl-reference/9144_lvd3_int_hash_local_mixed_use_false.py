r"""Test 9144 -- lvD3 (expected FAIL; proved under C2): a local read BOTH as an f-string part and
by `+`. CPython raises TypeError. One non-opaque read anywhere drops the local from C2.
"""
# pycsl-expected: FAIL
from __future__ import annotations


#@ no_exception \all
#@ assigns \nothing
def f(x: int) -> int:
    name = x
    name = "abc"
    s = f"*{name}"
    return name + len(s)


if __name__ == "__main__":
    try:
        print("result", f(3))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
