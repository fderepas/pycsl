r"""Test 5109 -- gen #37 route #226 increment 2c (expected FAIL): red team 29 a07, a separate `\length` CLAUSE next to an int clause (`self.x >= 0` / `\length(self.xs) >= 0`). PROVED at base; CPython `f(D(-1, []))` is -1. 2c states one goal over both clauses, which FAILS on the int one.
"""
# pycsl-expected: FAIL
from typing import List

#@ class invariant self.x >= 0
#@ class invariant \length(self.xs) >= 0
class D:
    def __init__(self, x: int, xs: List[int]) -> None:
        self.x = x
        self.xs = xs

#@ ensures \result >= 0
def f(d: D) -> int:
    return d.x

if __name__ == "__main__":
    assert f(D(-1, [])) == -1
