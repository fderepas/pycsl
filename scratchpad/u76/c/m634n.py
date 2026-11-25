from dataclasses import dataclass


@dataclass
class R:
    a: int
    b: int


#@ requires True
#@ ensures \result == r.a
#@ assigns \nothing
def f(r: R) -> int:
    s = 0
    i = 0
    #@ loop invariant 0 <= i <= 1
    #@ loop variant 1 - i
    while i < 1:
        s = s + r.b
        i = i + 1
    return r.a
