r"""Test 9477 -- lvO re.Match model (expected PASS): `m.re.groups` is the pattern's group count,
computed by CPython's own `re.compile` at emission (2 here). Twin: 9478 (must FAIL).
"""
# pycsl-expected: PASS
from __future__ import annotations
import re

_KV = re.compile(r"(\w+)=(\w+)")


#@ ensures \result == 2
#@ assigns \nothing
def ngroups(s: str) -> int:
    m = _KV.match(s)
    if m:
        return m.re.groups
    return 2


if __name__ == "__main__":
    for s in ["a=b", "x"]:
        r = ngroups(s)
        print("VIOLATION contract" if r != 2 else "result", r)
