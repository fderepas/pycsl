r"""Test 5108 -- gen #37 route #226 increment 2c (expected FAIL): red team 29 a06, an int conjunct AND a `\length` conjunct in ONE invariant (`self.x >= 0 and \length(self.xs) >= 0`), both fields from `__init__` parameters. No goal at base (the `\length` conjunct put the class out of the int-only projection), so `ensures \result >= 0` on `d.x` PROVED; CPython `f(D(-1, []))` is -1. 2c binds `xs` as an array and states `forall x : int, xs : array int. x = x -> xs = xs -> ..`, which FAILS.
"""
# pycsl-expected: FAIL
from typing import List

#@ class invariant self.x >= 0 and \length(self.xs) >= 0
class D:
    def __init__(self, x: int, xs: List[int]) -> None:
        self.x = x
        self.xs = xs

#@ ensures \result >= 0
def f(d: D) -> int:
    return d.x

if __name__ == "__main__":
    assert f(D(-1, [])) == -1
