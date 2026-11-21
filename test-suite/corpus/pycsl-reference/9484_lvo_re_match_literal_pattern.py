r"""Test 9484 -- lvO re.Match model (expected PASS): `re.match(<str literal>, s)` (stdlib `re`) binds
a match local over the literal pattern; both groups lie outside any repeat / alternation, so their `str`
reads need only the not-None VC the `if m:` guard discharges, and equal subjects give equal groups.
Twin: 9485 (must FAIL).
"""
# pycsl-expected: PASS
from __future__ import annotations
import re


#@ ensures \result == True
#@ assigns \nothing
def stable(s: str) -> bool:
    m = re.match(r"^([A-Za-z_]+)\[([A-Za-z_]+)\]$", s)
    n = re.match(r"^([A-Za-z_]+)\[([A-Za-z_]+)\]$", s)
    if m:
        if n:
            return m.group(2) == n.group(2)
        return False
    return True


if __name__ == "__main__":
    for s in ["Stack[int]", "x", ""]:
        r = stable(s)
        print("VIOLATION contract" if r is not True else "result", r)
