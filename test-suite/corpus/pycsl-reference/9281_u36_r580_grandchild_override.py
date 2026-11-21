r"""Test 9281 -- route #580 (expected FAIL: PROVED at base 822621340 in the default model, REFUSED PYCSL-R580-OVERRIDE-FRAME-AFTER-BASE-STUB in every model; red team 55 probe (u36 probe p580b)): the hidden write in a GRANDCHILD `T(S(C)).m` (route #278's MRO pairs, closed transitively); CPython caller(T(), same object) == 2 under `ensures \result == 1`
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
    pass


@mutable_state
class T(S):

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
        k = T()
        r = caller(k, k)
        print("VIOLATION contract" if r != 1 else "result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
