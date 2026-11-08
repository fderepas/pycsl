r"""Test 7943 -- route #500 (expected FAIL: PROVED at base, REFUSED PYCSL-R500-INLINE-NESTED-RETURN): the nested `return` sits in a method the inlined method calls on `self`; claimed 1, CPython 101 (rt44 g526/r52609)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional


class C:
    def __init__(self) -> None:
        self.v: int = 0

    def m(self, n: int) -> int:
        return self.k(n)

    def k(self, n: int) -> int:
        if n > 0:
            if n > 1:
                return 1
        return 2


g = C()


#@ ensures \result == 1
def f(n: int) -> int:
    r = g.m(5)
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
