r"""Test 9061 -- u30 route #568 (expected FAIL): as 9060 with the HONEST declaration `assigns self.a, self.flag`:
the label filter drops `flag` and the route #109 fallback fired only when it dropped EVERY target, so the stub
still wrote `self.a` alone. CPython (o is c): 2.
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

    #@ assigns self.a, self.flag
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
