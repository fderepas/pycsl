r"""Test 10521 -- run #9 u76, review rt84 F2, route #634 (owner side). f declares `#@ assigns \nothing` but
writes the field r.b of its record parameter inside a loop; g claims r.b unchanged. `cd <tree root> && python
<this file>` prints "CPython g(R(1,0)) = 5", the claim below is false. L21 failed safe here only because Why3
inferred the in-module `let` effect; the declared frame was never compared with the body. REFUSED:
PYCSL-FUNCTION-FRAME.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass


@dataclass
class R:
    a: int
    b: int


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
