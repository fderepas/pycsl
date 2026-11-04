r"""Test 8829 -- lvA module-constant str-pair loops (expected FAIL): the constant list is MUTATED
(`_STRIPS.append(...)`) before the loop, so it is not a constant and the unroll must not apply; the
appended pair grows the string and the claim must NOT prove (CPython: rewrite("q") is False: "q" -> "qq").
"""
# pycsl-expected: FAIL
from __future__ import annotations
from typing import List, Tuple

_STRIPS: List[Tuple[str, str]] = [("x", "y")]


#@ ensures \result == True
def rewrite(s: str) -> bool:
    _STRIPS.append(("q", "qq"))
    out = s.strip()
    n = len(out)
    for a, b in _STRIPS:
        out = out.replace(a, b)
    return len(out) == n


if __name__ == "__main__":
    r = rewrite("q")
    print("VIOLATION contract" if r is not True else "result", r)
