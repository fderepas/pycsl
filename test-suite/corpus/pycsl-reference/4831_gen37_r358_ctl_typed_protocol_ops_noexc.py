r"""Test 4831 -- gen #37 route #358: CONTROL: under `no_exception \all`, a record field read, `for` over `List[int]`, truth tests of `int` / `str` / `List[int]`, `"".join` of strings and a `self.h()` call in a field-less class carry no R358 assertion; PROVES (CPython 0).
"""
# pycsl-expected: PASS
from typing import List

class R:
    def __init__(self, v: int) -> None:
        self.v = v

class P:
    #@ ensures \result == 0
    def h(self) -> int:
        return 0

    #@ no_exception \all
    #@ ensures \result == 0
    def m(self, xs: List[int], n: int, s: str, r: R) -> int:
        c = r.v
        for e in xs:
            c = c + 1
        if n:
            c = c + 1
        t = "".join([s, "a"])
        if s:
            c = c + 1
        if xs:
            c = c + 1
        k = self.h()
        return k


if __name__ == "__main__":
    r = P().m([1, 2], 1, "x", R(3))
    assert r == 0, r
