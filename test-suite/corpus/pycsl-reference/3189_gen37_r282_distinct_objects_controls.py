r"""Test 3189 — route #282 CONTROLS (expected PASS): verified callers passing DISTINCT objects.

The callees of 3180 (two lists) and 3181 (two records) called from verified code with distinct fresh
objects: each caller claims the unchanged argument
(`b[0] == 1`, `y.v == 0` — what the callee's frame states), TRUE in CPython (see `__main__`), and PROVES — the PARAM-DISJOINT declaration does not cost an honest caller anything. 3185's method is
included and proves on its own; its verified callers fail closed even with a fresh list (the
constructor's stored list is havocked, R167), so `T([0]).m([5])` is checked only in `__main__`.
"""
# pycsl-expected: PASS
from typing import List


#@ requires len(xs) == 1 and len(ys) == 1
#@ ensures ys[0] == \old(ys[0])
#@ assigns xs[0]
def f(xs: List[int], ys: List[int]) -> None:
    xs[0] = ys[0] + 1


#@ ensures \result == 1
def two_lists() -> int:
    a = [1]
    b = [1]
    f(a, b)
    return b[0]


class A:
    def __init__(self) -> None:
        self.v: int = 0


#@ ensures b.v == \old(b.v)
#@ assigns a.v
def fa(a: A, b: A) -> None:
    a.v = b.v + 1


#@ ensures \result == 0
def two_records() -> int:
    x = A()
    y = A()
    fa(x, y)
    return y.v


class T:
    def __init__(self, ys: List[int]) -> None:
        self.ys: List[int] = ys

    #@ requires len(xs) == 1 and \length(self.ys) == 1 and self.ys[0] == 0
    #@ ensures \result == 0
    #@ assigns xs[0]
    def m(self, xs: List[int]) -> int:
        xs[0] = 7
        return self.ys[0]


if __name__ == "__main__":
    assert two_lists() == 1
    assert two_records() == 0
    assert T([0]).m([5]) == 0
