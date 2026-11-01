r"""Test 7942 -- route #500 (expected FAIL: PROVED at base, REFUSED PYCSL-R500-INLINE-NESTED-RETURN): a `return` inside a `for` of the method; `r = g.m(3); return r + 100` claimed 1, CPython 101
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional


class C:
    def __init__(self) -> None:
        self.v: int = 0

    def m(self, n: int) -> int:
        for i in range(n):
            return 1
        return 2


g = C()


#@ ensures \result == 1
def f(n: int) -> int:
    r = g.m(3)
    return r + 100


if __name__ == "__main__":
    try:
        r = f(0)
        if not (r == 1):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
