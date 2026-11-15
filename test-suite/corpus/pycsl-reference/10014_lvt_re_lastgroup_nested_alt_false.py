r"""Test 10014 -- lvT re-lastgroup (expected FAIL): the pattern's top level is ONE named group
wrapping an alternation whose second branch is an unnamed group: CPython's `lastgroup` is "A"
for both, but the gate's shape (every top-level alternative one named group) holds and the value
stays law-free, so the false claim `\result == "B"` is not proved (`kind("y")` is "A").
Control: 10010.
"""
# pycsl-expected: FAIL
from __future__ import annotations
import re

_P = re.compile(r"(?P<A>x|(y))")


#@ ensures \result == "B"
#@ assigns \nothing
def kind(s: str) -> str:
    m = _P.match(s, 0)
    if not m:
        return "B"
    return m.lastgroup


if __name__ == "__main__":
    r = kind("y")
    print("VIOLATION contract" if r != "B" else "result", r)
