r"""Test 9510 -- lvP (expected PASS): a function holding a lvO MATCH LOCAL (`m = re.match(<lit>, s)`) that
ALSO makes a call whose argument is a SUBSCRIPT (`len(s[1:])`). lvO's match-local scan compares every other
call's argument signature `(type, name, value)` against the binding's, and a Subscript's `value` is an IR
node (a dict): at base the comparison raised `TypeError` inside the emitter and the run ended
`UNEXPECTED PIPELINE ERROR: cannot use 'tuple' as a set element (unhashable type: 'dict')` (the shape of
`proof2why3/normalize.py::_alpha_rename`, whose `len(kv[0])` hit it). Such a signature cannot equal a
binding's (those hash), so it is skipped and the function is emitted and proved.
"""
# pycsl-expected: PASS
from __future__ import annotations
import re


#@ ensures \result >= 0
#@ assigns \nothing
def tail_len(s: str) -> int:
    m = re.match(r"(\w+)=", s)
    if m:
        return len(s[1:])
    return 0


if __name__ == "__main__":
    for s in ["a=b", "x", ""]:
        r = tail_len(s)
        print("VIOLATION contract" if not r >= 0 else "result", r)
