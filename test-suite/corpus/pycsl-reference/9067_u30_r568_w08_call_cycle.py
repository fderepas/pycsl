r"""Test 9067 -- u30 route #568 (expected FAIL): a call cycle (`m` -> `g` -> `c.m`): whichever member is emitted
first, a stub of `m` must not omit the `_pyobj_state` write its definition performs. CPython (o is c): 2.
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

    #@ \diverges
    #@ assigns self.a
    def m(self, v: int, o: Any) -> None:
        self.a = v
        self.flag = v
        if v > 100:
            g(self, v - 1, o)

#@ \diverges
#@ ensures \result == 1
#@ assigns c.a
def g(c: C, v: int, o: Any) -> int:
    c.m(0, o)
    x = getattr(o, "flag", 0)
    c.m(5, o)
    y = getattr(o, "flag", 0)
    if x or not y:
        return 1
    return 2

if __name__ == "__main__":
    k = C()
    print(g(k, 0, k))
