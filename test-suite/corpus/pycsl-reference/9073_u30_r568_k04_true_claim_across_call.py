r"""Test 9073 -- u30 route #568 (expected PASS): CONTROL: the 9063 shape (receiver `Any`, caller framing `c.flag`)
with a TRUE claim: framing the call with the cell loses no honest fact.
"""
# pycsl-expected: PASS
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

#@ ensures \result == 1 or \result == 2
#@ assigns c.flag
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
