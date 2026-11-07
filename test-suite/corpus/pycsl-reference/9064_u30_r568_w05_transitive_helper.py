r"""Test 9064 -- u30 route #568 (expected FAIL): the unresolved `c.m(..)` sits in a helper the reading function
calls: the helper's frame must carry the cell for the caller to see it. CPython (o is c): 2.
"""
# pycsl-expected: FAIL
from typing import Any
def mutable_state(cls):
    return cls

@mutable_state
class C:
    #@ \trusted reviewer: probe
    #@ assigns self.flag
    def __init__(self) -> None:
        pass

    #@ assigns self.flag
    def m(self, v: int) -> None:
        self.flag = v

#@ assigns c.flag
def helper(c: Any, v: int) -> None:
    c.m(v)

#@ ensures \result == 1
#@ assigns c.flag
def caller(c: Any, o: Any) -> int:
    helper(c, 0)
    x = getattr(o, "flag", 0)
    helper(c, 5)
    y = getattr(o, "flag", 0)
    if x or not y:
        return 1
    return 2

if __name__ == "__main__":
    k = C()
    print(caller(k, k))
