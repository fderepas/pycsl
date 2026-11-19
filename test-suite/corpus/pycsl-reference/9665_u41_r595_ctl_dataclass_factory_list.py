r"""Test 9665 -- route #595 CONTROL: a dataclass field `field(default_factory=list)` (a builtin constructor: plain data) and a call of the method by its `def` name; `\result == 5` rests on `m`'s contract (expected PASS: PROVED at base 4e6004f3b and at HEAD)
"""
# pycsl-expected: PASS
from typing import Any, List
from dataclasses import dataclass, field


@dataclass
class C:
    a: int = 0
    xs: List[int] = field(default_factory=list)

    #@ ensures self.a == v
    #@ assigns self.a
    def m(self, v: int) -> None:
        self.a = v


#@ requires c.a == 0
#@ ensures \result == 5
#@ assigns c.a
def caller(c: C) -> int:
    c.m(5)
    return c.a


if __name__ == "__main__":
    r = caller(C())
    print("result", r)
