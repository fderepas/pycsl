r"""Test 9297 -- route #580 CONTROL (expected PASS at base 822621340 and HEAD): R580's advice followed on 9280 -- the attribute the override writes is a FIELD the BASE class declares in `__init__`, listed in both methods' `#@ assigns` (route #278 compares the two frames), so a call through the base-typed receiver frames it and the honest claim about it proves
"""
# pycsl-expected: PASS
from typing import Any


def mutable_state(cls):
    return cls


@mutable_state
class C:
    #@ assigns \nothing
    def __init__(self) -> None:
        self.a: int = 0
        self.flag: int = 0

    #@ ensures self.flag == v
    #@ assigns self.a, self.flag
    def m(self, v: int) -> None:
        self.a = v
        self.flag = v


@mutable_state
class S(C):

    #@ ensures self.flag == v
    #@ assigns self.a, self.flag
    def m(self, v: int) -> None:
        self.a = v + 1
        self.flag = v


#@ ensures \result == 1
#@ assigns c.a, c.flag
def caller(c: C) -> int:
    c.m(0)
    x = c.flag
    c.m(5)
    y = c.flag
    if x == 0 and y == 5:
        return 1
    return 2


if __name__ == "__main__":
    print("result", caller(S()), caller(C()))
