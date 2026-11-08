r"""Test 4632 -- gen #37 route #343: CONTROL: builtins on non-erased arguments (`range(n)`, `len(xs)`, `max(n, 0)` on `int` / `List[int]`) under `no_exception \all` are not touched by the R343 assertion (only an erased argument is); PROVES `\result >= 0` (CPython 2).
"""
# pycsl-expected: PASS
from typing import List

#@ requires n >= 0
#@ no_exception \all
#@ ensures \result >= 0
def m(n: int, xs: List[int]) -> int:
    r = range(n)
    k = len(xs)
    return max(n, 0) + k

if __name__ == "__main__":
    assert m(2, []) == 2
