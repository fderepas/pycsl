r"""Test 9666 -- route #595 CONTROL, R595's first advice followed: the class body keeps a `match` capture but the caller calls the method by the name of its `def` (`c.m(5)`); `\result == 5` rests on `m`'s contract (expected PASS: PROVED at base 4e6004f3b and at HEAD)
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

    match 3:
        case n:
            pass


#@ requires c.a == 0
#@ ensures \result == 5
#@ assigns c.a
def caller(c: C) -> int:
    c.m(5)
    return c.a


if __name__ == "__main__":
    r = caller(C())
    print("result", r)
