r"""Test 7970 -- route #501 (control, expected PASS): a class K defines `index` / `format`; g calls them on a `K` parameter and on `K()`; f catches ValueError / KeyError around g; g returns `n + 10`, `ensures \result == n + 10`; CPython f(5) returns 15
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional

class K:
    def __init__(self) -> None:
        self.v = 0

    #@ ensures \result == x
    def index(self, x: int) -> int:
        return x

    #@ ensures \result == x + 1
    def format(self, x: int) -> int:
        return x + 1


#@ ensures \result == n + 10
def g(k: K, n: int) -> int:
    a = k.index(1)
    b = K().index(2)
    e = k.format(3)
    return n + 10


#@ ensures \result == n + 10
def f(n: int) -> int:
    try:
        return g(K(), n)
    except ValueError:
        return 0
    except KeyError:
        return 0


if __name__ == "__main__":
    assert f(5) == 15
