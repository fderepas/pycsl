r"""Test 8828 -- lvA module-constant str-pair loops (expected FAIL): the tuple target `b` is READ after the
loop (Python leaves it bound to the LAST pair), so the loop is NOT unrolled (the unroll never binds the
targets) and the false claim must NOT prove (CPython: rewrite("") is False: len("" + "yy") == 2).
"""
# pycsl-expected: FAIL
from __future__ import annotations
from typing import List, Tuple

_STRIPS: List[Tuple[str, str]] = [("x", "y"), ("z", "yy")]


#@ ensures \result == True
#@ assigns \nothing
def rewrite(s: str) -> bool:
    out = s.strip()
    n = len(out)
    for a, b in _STRIPS:
        out = out.replace(a, a)
    return len(out + b) == n


if __name__ == "__main__":
    r = rewrite("")
    print("VIOLATION contract" if r is not True else "result", r)
