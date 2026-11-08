r"""Test 9285 -- route #582 (expected FAIL: PROVED at base 822621340 in the default model, REFUSED PYCSL-R582-CLASS-BODY-ALIAS-CALL in every model; red team 55 probe gv1600_cls_alias_typed.py): an alias of a method with a hidden `self.flag` store, called on a `C`-typed receiver between two `getattr(o, "flag", 0)` reads; CPython caller(k, k) == 2 under `ensures \result == 1`
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
        self.flag = v

    n = m


#@ ensures \result == 1
#@ assigns c.a
def caller(c: C, o: Any) -> int:
    c.n(0)
    x = getattr(o, "flag", 0)
    c.n(5)
    y = getattr(o, "flag", 0)
    if x or not y:
        return 1
    return 2


if __name__ == "__main__":
    try:
        k = C()
        r = caller(k, k)
        if r != 1:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
