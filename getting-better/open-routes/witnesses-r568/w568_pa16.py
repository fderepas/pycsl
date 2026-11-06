"""probe pa16 (pa14 with truthiness; CPython x = 0 falsy, y = 5 truthy -> 2): record class C (field a); m declares `assigns self.a` but also stores self.flag (non-record -> setattr on the coarse cell). The caller-side val of m drops the cell, so two state-keyed reads of o.flag across the call are one term. CPython (o is c): x = 1, y = 2, returns 2."""
from typing import Any
def mutable_state(cls):
    return cls

@mutable_state
class C:
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def __init__(self) -> None:
        self.a: int = 0

    #@ requires True
    #@ ensures True
    #@ assigns self.a
    def m(self, v: int) -> None:
        self.a = v
        self.flag = v

#@ requires True
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
