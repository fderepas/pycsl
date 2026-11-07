r"""Test 8824 -- lvA compiled-pattern receiver (expected FAIL): the local `p` is bound TWICE, so `p.sub`
is NOT known to be the method of `re.compile(r"a")` (the second binding wins). The compiled-local
recognizer requires exactly one binding; were it to take the first, determinism would prove the false
claim (CPython: s = "b" gives "x" from the r"b" pattern vs "b").
"""
# pycsl-expected: FAIL
from __future__ import annotations
import re


#@ ensures \result == True
#@ assigns \nothing
def rebound(s: str) -> bool:
    p = re.compile(r"a")
    p = re.compile(r"b")
    return p.sub("x", s) == re.sub(r"a", "x", s)


if __name__ == "__main__":
    r = rebound("b")
    print("VIOLATION contract" if r is not True else "result", r)
