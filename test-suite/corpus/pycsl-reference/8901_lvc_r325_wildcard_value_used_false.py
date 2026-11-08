r"""Test 8901 -- lvC R325 wildcard (expected FAIL): false twin of 8900. The RESULT of `warnings.warn`
(CPython: `None`) is bound and used as an integer: `r + 1` raises TypeError in CPython, and the opaque int
fallback would "prove" `\result == r + 1`-style int facts of it. Route #325 must still refuse: the
wildcard fix exempts only the `_` PATTERN token, never a named binding of the value.
"""
# pycsl-expected: FAIL
from __future__ import annotations
import warnings


#@ ensures \result == 1
#@ assigns \nothing
def warn_value(d: dict, seen: set) -> int:
    k = d.get("name", 0)
    r = 0
    if k in seen:
        r = warnings.warn("member")
    return r * 0 + 1


if __name__ == "__main__":
    try:
        print("result", warn_value({"name": 3}, {3}))
    except TypeError as e:
        print("VIOLATION contract (TypeError)", e)
