r"""Test 9478 -- lvO re.Match model (expected FAIL): false twin of 9477 (`m.re.groups` is 2, not 1).
"""
# pycsl-expected: FAIL
from __future__ import annotations
import re

_KV = re.compile(r"(\w+)=(\w+)")


#@ ensures \result == 1
#@ assigns \nothing
def ngroups(s: str) -> int:
    m = _KV.match(s)
    if m:
        return m.re.groups
    return 1


if __name__ == "__main__":
    r = ngroups("a=b")
    print("VIOLATION contract" if r != 1 else "result", r)
