r"""Test 9659 -- route #595 (expected FAIL: PROVED at base 4e6004f3b in the default model, REFUSED PYCSL-R595-CLASS-BODY-BINDING-CALL in every model at HEAD): u41 probe: an `as` on an or-pattern, then an irrefutable capture `case n:` in the class body; CPython 5 under `ensures \result == 0`
"""
# pycsl-expected: FAIL
from typing import Any
from dataclasses import dataclass, field


class C:
    def __init__(self) -> None:
        self.a: int = 0

    #@ ensures self.a == v
    #@ assigns self.a
    def m(self, v: int) -> None:
        self.a = v

    match m:
        case (0 | 1) as q:
            pass
        case n:
            pass


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
