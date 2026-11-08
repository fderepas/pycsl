r"""Test 9294 -- route #582 CONTROL (expected PASS at base 822621340 and HEAD): R582's second advice followed on 9283: `n` defined with its own `def` (and contract) calling `m`, so `c.n(5)` resolves to it and `\result == 5` proves
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
    print("result", caller(C()))
