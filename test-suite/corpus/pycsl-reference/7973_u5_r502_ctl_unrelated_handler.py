r"""Test 7973 -- route #502 (control, expected PASS): g's `[10 // (v * v + 1) for v in xs]` (a non-literal divisor: summarised as ZeroDivisionError only); f catches KeyError (not ZeroDivisionError); `ensures \result == len(xs)`; CPython f([1, 2]) returns 2
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional

#@ ensures \result == len(xs)
def g(xs: List[int]) -> int:
    ys = [10 // (v * v + 1) for v in xs]
    return len(xs)


#@ ensures \result == len(xs)
def f(xs: List[int]) -> int:
    try:
        return g(xs)
    except KeyError:
        return 0


if __name__ == "__main__":
    assert f([1, 2]) == 2
