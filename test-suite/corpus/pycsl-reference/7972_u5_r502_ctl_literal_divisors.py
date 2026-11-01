r"""Test 7972 -- route #502 (control, expected PASS): g's comprehensions / lambda / genexp divide only by non-zero literals and raise to a non-negative literal power (`[v // 2 ...]`, `{v: v % 3 ...}`, `sorted(xs, key=lambda v: -v)`, `sum(v ** 2 ...)`); f catches ZeroDivisionError; `ensures \result == 1`; CPython f([0, 5]) returns 1
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional

#@ ensures \result == 1
def g(xs: List[int]) -> int:
    ys = [v // 2 for v in xs]
    d = {v: v % 3 for v in xs}
    zs = sorted(xs, key=lambda v: -v)
    t = sum(v ** 2 for v in xs)
    return 1


#@ ensures \result == 1
def f(xs: List[int]) -> int:
    try:
        return g(xs)
    except ZeroDivisionError:
        return 0


if __name__ == "__main__":
    assert f([0, 5]) == 1
