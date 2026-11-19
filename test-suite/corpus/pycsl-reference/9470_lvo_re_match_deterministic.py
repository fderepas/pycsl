r"""Test 9470 -- lvO re.Match model (expected PASS): two MATCH LOCALS bound by the SAME module-constant
compiled pattern on the SAME subject read the SAME group. The law-free model claims only that a match is a
deterministic function of (pattern, subject, pos) -- exact, because a match local never escapes (no
`==` / `is` / argument / return), so CPython's fresh-object identity is unobservable. At base both reads
were the receiver-less opaque `m_group_1 1` (a facade). Twin: 9471 (must FAIL).
"""
# pycsl-expected: PASS
from __future__ import annotations
import re

_KV = re.compile(r"(\w+)=(\w+)")


#@ ensures \result == True
#@ assigns \nothing
def same_key(s: str) -> bool:
    m = _KV.match(s)
    n = _KV.match(s)
    if m:
        if n:
            return m.group(1) == n.group(1)
        return False
    return True


if __name__ == "__main__":
    for s in ["a=b", "key=val", "", "=x", "x"]:
        r = same_key(s)
        print("VIOLATION contract" if r is not True else "result", r)
