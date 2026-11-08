r"""Test 9282 -- route #580 CONTROL (expected PASS at base 822621340 and HEAD): the same shape with an HONEST override (`S.m` writes `self.a` only, no hidden attribute): the base stub's frame is the union of the overrides' frames, no override writes object state, the two `getattr` reads around the calls are one value and `\result == 1` proves
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def mutable_state(cls):
    return cls


@mutable_state
class C:
    #@ assigns \nothing
    def __init__(self) -> None:
        self.a: int = 0

    #@ assigns self.a
    def m(self, v: int) -> None:
        self.a = v


@mutable_state
class S(C):

    #@ assigns self.a
    def m(self, v: int) -> None:
        self.a = v + 1


#@ ensures \result == 1
#@ assigns c.a
def caller(c: C, o: Any) -> int:
    c.m(0)
    x = getattr(o, "flag", 0)
    c.m(5)
    y = getattr(o, "flag", 0)
    if x or not y:
        return 1
    return 2


if __name__ == "__main__":
    k = S()
    print("result", caller(k, k))
