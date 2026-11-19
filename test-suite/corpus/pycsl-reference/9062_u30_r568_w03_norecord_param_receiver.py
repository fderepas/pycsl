r"""Test 9062 -- u30 route #568 (expected FAIL): a class with NO record (`type c = int`); the receiver is a
PARAMETER `c: C`, not resolved to a method table, so `c.m(..)` minted a frameless (pure) stub and the two
state-keyed reads collapsed. CPython (o is c): 2.
"""
# pycsl-expected: FAIL
from typing import Any
def mutable_state(cls):
    return cls

@mutable_state
class C:
    #@ \trusted reviewer: probe
    #@ assigns self.a, self.flag
    def __init__(self) -> None:
        pass

    #@ assigns self.flag
    def m(self, v: int) -> None:
        self.flag = v

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
