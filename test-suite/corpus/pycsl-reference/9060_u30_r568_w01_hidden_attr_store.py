r"""Test 9060 -- u30 route #568 (expected FAIL): record class `C {a}`; `m` declares `assigns self.a` and ALSO
stores `self.flag` (an attribute the record does not carry: a `setattr` on the coarse `_pyobj_state` cell).
The definition's frame is `writes { self.a, _pyobj_state }`, the caller-side stub's was `writes { self.a }`,
so two state-keyed `getattr(o, "flag", 0)` reads around `c.m(..)` were one term and `\result == 1` PROVED.
CPython (o is c): 2.
"""
# pycsl-expected: FAIL
from typing import Any
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
    k = C()
    print(caller(k, k))
