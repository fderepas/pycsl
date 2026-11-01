r"""Test 7988 -- route #505 (expected FAIL: Why3 type error at base, REFUSED PYCSL-R505-INLINE-BARE-SELF by name): `m(self): x = self; return x.v` spliced into a method; claimed 2, CPython f(0) returns 1
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional


class C:
    def __init__(self, v: int) -> None:
        self.v = v

    def m(self) -> int:
        x = self
        return x.v

    #@ ensures \result == self.v
    def run(self) -> int:
        return g.m()


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
