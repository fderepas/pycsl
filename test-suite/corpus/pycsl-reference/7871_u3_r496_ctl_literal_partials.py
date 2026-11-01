r"""Test 7871 -- route #496 (control, expected PASS): g calls the partial builtins only on arguments that cannot raise (`chr(65)`, `range(0, n, 2)`, `max(n, 0)`, `pow(n, 2)`); f catches ValueError; CPython f([], 3) returns 1
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional

#@ ensures \result == 1
def g(xs: List[int], n: int) -> int:
    c = chr(65)
    r = len(range(0, n, 2))
    m = max(n, 0)
    p = pow(n, 2)
    return 1


#@ ensures \result == 1
def f(xs: List[int], n: int) -> int:
    try:
        return g(xs, n)
    except ValueError:
        return 2


if __name__ == "__main__":
    assert f([], 3) == 1 and f([4, 5], 0) == 1
