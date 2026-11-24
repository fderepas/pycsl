from dataclasses import dataclass


@dataclass
class R:
    a: int
    b: int


#@ requires True
#@ ensures True
#@ assigns \nothing
def f(r: R) -> int:
    r.b = 5
    return r.a


#@ requires True
#@ ensures \result == 0
def g() -> int:
    r = R(1, 0)
    f(r)
    return r.b
