r"""Test 9481 -- lvO re.Match model (expected PASS): a tokenizer loop over `_T.match(fmt, pos)` /
`m.end()` terminates under a DEFENSIVE guard (`e <= pos` -> stop) -- no regex law is claimed, so the
guard (dead in CPython: this pattern always consumes a character) is what makes the variant provable.
Twin: 9482 (must FAIL).
"""
# pycsl-expected: PASS
from __future__ import annotations
import re

_T = re.compile(r"(\d*)([a-z])")


#@ ensures \result >= 0
#@ assigns \nothing
def ntokens(fmt: str) -> int:
    pos = 0
    n = 0
    #@ loop invariant n >= 0
    #@ loop variant len(fmt) - pos
    while pos < len(fmt):
        m = _T.match(fmt, pos)
        if not m:
            return n
        e = m.end()
        if e <= pos:
            return n
        n = n + 1
        pos = e
    return n


if __name__ == "__main__":
    for s in ["a2b3c", "", "9"]:
        r = ntokens(s)
        print("VIOLATION contract" if r < 0 else "result", r)
