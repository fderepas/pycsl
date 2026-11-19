r"""Test 9280 -- route #580 (expected FAIL: PROVED at base 822621340 in the default model, REFUSED PYCSL-R580-OVERRIDE-FRAME-AFTER-BASE-STUB in every model; red team 55 probe gi1600_override_sub.py): `S(C).m` overrides `C.m` (both `assigns self.a`) with a hidden `self.flag = v`; `caller(c: C, o)` reads `getattr(o, "flag", 0)` around two `c.m(..)`: the base stub `c_m_1` wrote `self.c_a` only, so the two reads were one term; CPython caller(S(), same object) == 2 under `ensures \result == 1`
"""
# pycsl-expected: FAIL
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
        self.a = v
        self.flag = v


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
    try:
        k = S()
        r = caller(k, k)
        if r != 1:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
