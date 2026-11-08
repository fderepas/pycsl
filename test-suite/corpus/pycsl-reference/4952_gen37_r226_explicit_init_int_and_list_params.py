r"""Test 4952 -- gen #37 route #226 (expected FAIL): witness q362xinit: explicit `__init__(self, x: int, xs: List[int])` storing both, no `#@ requires`, under `#@ class invariant self.x >= 0`; the `List` parameter put the class outside increment 2 (no goal; `ensures \result >= 0` on `d.x` PROVED; CPython `D(-1, []).x` is -1). The projection states `forall x. x = x -> x >= 0`, which FAILS.
"""
# pycsl-expected: FAIL
from typing import List

#@ class invariant self.x >= 0
class D:
    def __init__(self, x: int, xs: List[int]) -> None:
        self.x = x
        self.xs = xs

#@ ensures \result >= 0
def f(d: D) -> int:
    return d.x

if __name__ == "__main__":
    assert f(D(-1, [])) == -1
