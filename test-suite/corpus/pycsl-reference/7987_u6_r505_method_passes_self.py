r"""Test 7987 -- route #505 (expected FAIL: PROVED at base, REFUSED PYCSL-R505-INLINE-BARE-SELF): `m(self): return getv(self)` spliced into the method `run` kept `self`, read as run's receiver; claimed 2, CPython f(0) returns 1 (rt45 g603/d60305)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional


class C:
    def __init__(self, v: int) -> None:
        self.v = v

    def m(self) -> int:
        return getv(self)

    #@ ensures \result == self.v
    def run(self) -> int:
        return g.m()


#@ ensures \result == c.v
def getv(c: C) -> int:
    return c.v


g = C(1)


#@ ensures \result == 2
def f(n: int) -> int:
    c = C(2)
    return c.run()


if __name__ == "__main__":
    try:
        r = f(0)
        if not (r == 2):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
