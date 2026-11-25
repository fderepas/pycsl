from dataclasses import dataclass


@dataclass
class R:
    a: int
    b: int


#@ requires True
#@ ensures \result == r.a
#@ assigns \nothing
def f(r: R) -> int:
    i = 0
    #@ loop invariant 0 <= i <= 1
    #@ loop variant 1 - i
    while i < 1:
        r.b = 5
        i = i + 1
    return r.a


#@ requires r.b == 0
#@ ensures \result == 0
def g(r: R) -> int:
    f(r)
    return r.b


if __name__ == "__main__":
    print("CPython g(R(1,0)) =", g(R(1, 0)))
