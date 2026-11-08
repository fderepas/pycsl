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
        self.b: int = 0

    #@ requires True
    #@ ensures True
    #@ assigns self.a
    def m(self, v: int) -> None:
        self.a = v


@mutable_state
class S(C):

    #@ requires True
    #@ ensures True
    #@ assigns self.a, self.b
    def m(self, v: int) -> None:
        self.a = v
        self.b = v


#@ requires c.b == 0
#@ ensures \result == 0
#@ assigns c.a
def caller(c: C) -> int:
    c.m(5)
    return c.b
