r"""Test 8903 -- lvC R325 wildcard (expected FAIL): false twin of 8900 -- the shape is admitted now, and a
CPython-false postcondition over it must not prove (`warn_if_member(.., 7)` returns 7, not 8).
"""
# pycsl-expected: FAIL
from __future__ import annotations
import warnings


#@ ensures \result == n + 1
#@ assigns \nothing
def warn_if_member(d: dict, seen: set, n: int) -> int:
    k = d.get("name", 0)
    if k in seen:
        warnings.warn("member")
    return n


if __name__ == "__main__":
    r = warn_if_member({"name": 3}, {3}, 7)
    print("VIOLATION contract" if r != 8 else "result", r)
