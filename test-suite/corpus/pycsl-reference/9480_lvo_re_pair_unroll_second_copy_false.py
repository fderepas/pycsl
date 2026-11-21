r"""Test 9480 -- lvO seq_rx unroll (expected FAIL): false twin of 9479. The SECOND unrolled copy is
reachable (the first pattern may fail and the second match), so `\result != "b"` must NOT prove
(CPython: "bx" gives "b").
"""
# pycsl-expected: FAIL
from __future__ import annotations
import re

_A = re.compile(r"a(\w)")
_B = re.compile(r"b(\w)")
_PAIRS = (("a", _A), ("b", _B))


#@ ensures \result != "b"
#@ assigns \nothing
def kind(s: str) -> str:
    for kw, rx in _PAIRS:
        m = rx.match(s)
        if m:
            return kw
    return ""


if __name__ == "__main__":
    r = kind("bx")
    print("VIOLATION contract" if r == "b" else "result", r)
