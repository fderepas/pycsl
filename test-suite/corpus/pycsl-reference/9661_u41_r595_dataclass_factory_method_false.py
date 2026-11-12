r"""Test 9661 -- route #595 (expected FAIL: REFUSED (the method / instance-attribute shadowing rule, `c.n(...)` with a field `n`) at base 4e6004f3b in the default model, REFUSED PYCSL-R595-CLASS-BODY-BINDING-CALL in every model at HEAD): u41 probe: `@dataclass` with `n: Any = field(default_factory=lambda: C.m)`: the instance field is the function `C.m`, `c.n(c, 5)` writes `c.a`; CPython 5 under `ensures \result == 0`
"""
# pycsl-expected: FAIL
from typing import Any
from dataclasses import dataclass, field


@dataclass
class C:
    a: int = 0
    n: Any = field(default_factory=lambda: C.m)

    #@ ensures self.a == v
    #@ assigns self.a
    def m(self, v: int) -> None:
        self.a = v


#@ requires c.a == 0
#@ ensures \result == 0
#@ assigns c.a
def caller(c: C) -> int:
    c.n(c, 5)
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
