r"""Test 2978 — route #274 CONTROL (expected PASS): what the repair must NOT touch — a
comprehension / generator over a callee that declares `assigns \nothing`, one whose frame is
undeclared but whose body writes nothing, and a NON-mutating method on a receiver
(`xs.count(y)`), followed by a direct (modelled) call to the WRITING callee.
CPython: 5.
"""
# pycsl-expected: PASS
from typing import List

class C:
    def __init__(self) -> None:
        self.v: int = 0

#@ ensures \result == 2 * k
#@ assigns \nothing
def dbl(k: int) -> int:
    return 2 * k

#@ ensures \result == k + 1
def inc(k: int) -> int:
    return k + 1

#@ ensures \result == 1 and c.v == 5
#@ assigns c.v
def push(c: C) -> int:
    c.v = 5
    return 1

#@ requires c.v == 0
#@ ensures \result == 5
#@ assigns c.v
def f(c: C) -> int:
    xs: List[int] = [1, 2]
    ys = [dbl(y) for y in xs]
    s = sum(inc(y) for y in xs)
    zs = [xs.count(y) for y in xs]
    push(c)
    return c.v

if __name__ == "__main__":
    print(f(C()))
