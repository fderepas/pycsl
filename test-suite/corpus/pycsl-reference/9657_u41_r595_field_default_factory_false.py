r"""Test 9657 -- route #595 (expected FAIL: PROVED at base 4e6004f3b in the default model, REFUSED PYCSL-R595-CLASS-BODY-BINDING-CALL in every model at HEAD): red team rt56 probe hh1729: `n: Any = field(default_factory=lambda: m)` counted as plain data (route #582 read only `default`); CPython raises TypeError under `ensures \result == 0`
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def mutable_state(cls): return cls
from dataclasses import field

class C:
    def __init__(self) -> None:
        self.a: int = 0

    #@ ensures self.a == v
    #@ assigns self.a
    def m(self, v: int) -> None:
        self.a = v

    n: Any = field(default_factory=lambda: m)


#@ requires c.a == 0
#@ ensures \result == 0
#@ assigns c.a
def caller(c: C) -> int:
    c.n(5)
    return c.a


if __name__ == "__main__":
    try:
        r = caller(C())
        if r != 0:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
