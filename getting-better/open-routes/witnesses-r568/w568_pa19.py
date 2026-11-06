"""probe pa19 CONTROL (pa16 shape, class with NO record: trusted __init__, coarse cell in the val frame): record class C (field a); m declares `assigns self.a` but also stores self.flag (non-record -> setattr on the coarse cell). The caller-side val of m drops the cell, so two state-keyed reads of o.flag across the call are one term. CPython (o is c): x = 1, y = 2, returns 2."""
from typing import Any
def mutable_state(cls):
    return cls

@mutable_state
class C:
    #@ \trusted reviewer: probe
    #@ requires True
    #@ ensures True
    #@ assigns self.a, self.flag
    def __init__(self) -> None:
        pass

    #@ requires True
    #@ ensures True
    #@ assigns self.flag
    def m(self, v: int) -> None:
        self.flag = v

#@ requires True
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
