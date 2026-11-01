r"""Test 7872 -- route #496 (control, expected PASS): g calls a program helper h (arithmetic only) and a program class constructor; f catches ValueError; the chain holds no unlisted call; CPython f(3) returns 1
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional

class P:
    def __init__(self, v: int) -> None:
        self.v = v


#@ ensures \result == n + 1
def h(n: int) -> int:
    return n + 1


#@ ensures \result == 1
def g(n: int) -> int:
    k = h(n)
    p = P(k)
    return 1


#@ ensures \result == 1
def f(n: int) -> int:
    try:
        return g(n)
    except ValueError:
        return 2


if __name__ == "__main__":
    assert f(3) == 1
