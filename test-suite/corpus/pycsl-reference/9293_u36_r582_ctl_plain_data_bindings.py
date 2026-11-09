r"""Test 9293 -- route #582 CONTROL (expected PASS at base 822621340 and HEAD): class-body bindings of PLAIN DATA (`K = 3`, `n = 0`, `L: int = -1`) are not methods, so a call of the real method `c.m(5)` is not refused and its contract gives `\result == 5` (= R582's advice 'call the method by the name of its `def`' followed on 9283)
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass


class C:
    def __init__(self) -> None:
        self.a: int = 0

    #@ ensures self.a == v
    #@ assigns self.a
    def m(self, v: int) -> None:
        self.a = v

    K = 3
    n = 0
    L: int = -1


#@ requires c.a == 0
#@ ensures \result == 5
#@ assigns c.a
def caller(c: C) -> int:
    c.m(5)
    return c.a


if __name__ == "__main__":
    print("result", caller(C()))
