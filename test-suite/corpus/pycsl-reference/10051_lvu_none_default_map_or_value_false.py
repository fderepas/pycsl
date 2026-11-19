r"""Test 10051 -- lvU none-default map parameter `x or {}` (expected FAIL): `d = d or {}` is the
map `d` itself, not the empty map, so the claim `\result == 0` is false (CPython: `g("a", {"a": 3})`
is 3). Control: 10050.
"""
# pycsl-expected: FAIL
from typing import Dict, Optional


#@ ensures \result == 0
#@ assigns \nothing
def g(k: str, d: Optional[Dict[str, int]] = None) -> int:
    d = d or {}
    v = d.get(k, 0)
    if v < 0:
        return 0
    return v


if __name__ == "__main__":
    r = g("a", {"a": 3})
    print("VIOLATION contract" if r != 0 else "result", r)
