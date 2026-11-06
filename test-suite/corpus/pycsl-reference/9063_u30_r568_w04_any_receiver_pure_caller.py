r"""Test 9063 -- u30 route #568 (expected FAIL): as 9062 with the receiver typed `Any` and the caller declaring
`assigns \nothing`: the frameless stub made the caller pure, and its reads took route #213's unkeyed form. Now
the stub writes `_pyobj_state` and the `assigns \nothing` frame is rejected. CPython (o is c): 2.
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
#@ assigns \nothing
def caller(c: Any, o: Any) -> int:
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
