from __future__ import annotations


class A:
    def __init__(self) -> None:
        self.v = 0

    #@ requires n >= 0
    #@ ensures \result >= 0
    #@ \variant n
    def m(self, b: B, n: int) -> int:
        if n <= 0:
            return 0
        r: int = b.n(self, n - 1)
        return r


class B:
    def __init__(self) -> None:
        self.w = 0

    #@ requires k >= 0 and k < 0
    #@ ensures \result == 99
    #@ \variant k
    def n(self, a: A, k: int) -> int:
        if k <= 0:
            return 1
        r: int = a.m(self, k - 1)
        return r
