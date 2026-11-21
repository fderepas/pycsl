r"""Test 7941 -- route #500 (expected FAIL: PROVED at base, REFUSED PYCSL-R500-INLINE-NESTED-RETURN): the statement-position call skipped the caller's later field write; claimed `g.v == 0`, CPython 4 (rt44 g526/r52604)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional


class C:
    def __init__(self) -> None:
        self.v: int = 0

    def m(self, n: int) -> int:
        if n > 0:
            return 1
        return 2


g = C()


#@ ensures g.v == 0
def f(n: int) -> int:
    g.v = 0
    g.m(5)
    g.v = 4
    return 0


if __name__ == "__main__":
    try:
        r = (f(0), g.v)[1]
        if not (r == 0):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
