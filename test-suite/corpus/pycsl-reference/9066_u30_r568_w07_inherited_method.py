r"""Test 9066 -- u30 route #568 (expected FAIL): `m` is defined on the base `B` and called on a `C(B)` receiver:
the key `c__m` is absent from the method tables, so the call was an unresolved frameless stub. CPython (o is
c): 2.
"""
# pycsl-expected: FAIL
from typing import Any
def mutable_state(cls):
    return cls

@mutable_state
class B:
    #@ \trusted reviewer: probe
    #@ assigns self.flag
    def __init__(self) -> None:
        pass

    #@ assigns self.flag
    def m(self, v: int) -> None:
        self.flag = v

@mutable_state
class C(B):
    pass

#@ ensures \result == 1
#@ assigns c.flag
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
