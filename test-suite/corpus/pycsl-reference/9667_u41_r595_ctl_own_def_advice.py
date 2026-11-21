r"""Test 9667 -- route #595 CONTROL, R595's second advice followed: `n` is its own `def` (with a contract) that calls `m`; `\result == 5` rests on the two contracts (expected PASS: PROVED at base 4e6004f3b and at HEAD)
"""
# pycsl-expected: PASS
from typing import Any


class C:
    def __init__(self) -> None:
        self.a: int = 0

    #@ ensures self.a == v
    #@ assigns self.a
    def m(self, v: int) -> None:
        self.a = v

    #@ ensures self.a == v
    #@ assigns self.a
    def n(self, v: int) -> None:
        self.m(v)


#@ requires c.a == 0
#@ ensures \result == 5
#@ assigns c.a
def caller(c: C) -> int:
    c.n(5)
    return c.a


if __name__ == "__main__":
    r = caller(C())
    print("result", r)
