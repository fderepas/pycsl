r"""Test 9482 -- lvO re.Match model (expected FAIL): 9481 WITHOUT the defensive guard. `m.end()` is a
law-free read, so `pos = m.end()` need not advance and the variant must NOT prove (the model claims no
regex semantics, in particular not that a match consumes a character).
"""
# pycsl-expected: FAIL
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
        n = n + 1
        pos = m.end()
    return n


if __name__ == "__main__":
    print("result", ntokens("a2b3c"))
