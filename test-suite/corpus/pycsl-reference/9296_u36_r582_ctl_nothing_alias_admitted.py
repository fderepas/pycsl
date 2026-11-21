r"""Test 9296 -- route #582 CONTROL (expected PASS at base 822621340 and HEAD): a class-body alias of a method whose verified frame is `#@ assigns \nothing` (`n = m`) writes no field, so R582 admits the call `c.n(5)` (its receiver-less effect-free modelling is sound for it) and `c.a` unchanged across it proves
"""
# pycsl-expected: PASS
from typing import Any


class C:
    def __init__(self) -> None:
        self.a: int = 0

    #@ ensures \result == v + 1
    #@ assigns \nothing
    def m(self, v: int) -> int:
        return v + 1

    n = m


#@ requires c.a == 3
#@ ensures \result == 3
#@ assigns \nothing
def caller(c: C) -> int:
    c.n(5)
    return c.a


if __name__ == "__main__":
    k = C()
    k.a = 3
    print("result", caller(k))
