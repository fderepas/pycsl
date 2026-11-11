r"""Test 9479 -- lvO seq_rx unroll (expected PASS): `for kw, rx in _PAIRS` over a module constant of
`(str literal, compiled-pattern constant)` pairs is unrolled one copy per pair (`kw` -> its literal,
`rx.match` -> the constant's `.match`), with the early `return` in the body: the result is one of the
pair keywords or "". Twin: 9480 (must FAIL).
"""
# pycsl-expected: PASS
from __future__ import annotations
import re

_A = re.compile(r"a(\w)")
_B = re.compile(r"b(\w)")
_PAIRS = (("a", _A), ("b", _B))


#@ ensures \result == "" or \result == "a" or \result == "b"
#@ assigns \nothing
def kind(s: str) -> str:
    for kw, rx in _PAIRS:
        m = rx.match(s)
        if m:
            return kw
    return ""


if __name__ == "__main__":
    for s in ["ax", "bx", "cx", ""]:
        r = kind(s)
        print("VIOLATION contract" if r not in ("", "a", "b") else "result", r)
