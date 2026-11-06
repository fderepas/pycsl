r"""Test 9149 -- lvD3 (expected FAIL; proved under C2): `not name` after `name = ""` -- CPython True,
returns 0; C2 decided the hash nonzero. A `not` read drops the local from C2.
"""
# pycsl-expected: FAIL
from __future__ import annotations


#@ ensures \result == 1
#@ assigns \nothing
def f(x) -> int:
    name = x
    name = ""
    return 0 if not name else 1


if __name__ == "__main__":
    r = f(3)
    print("VIOLATION contract" if r != 1 else "result", r)
