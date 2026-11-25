from dataclasses import dataclass


@dataclass
class R:
    a: int
    b: int


#@ requires True
#@ ensures \result == r.a
#@ assigns r.b
def f(r: R) -> int:
    i = 0
    #@ loop invariant 0 <= i <= 1
    #@ loop variant 1 - i
    while i < 1:
        r.b = 5
        i = i + 1
    return r.a
