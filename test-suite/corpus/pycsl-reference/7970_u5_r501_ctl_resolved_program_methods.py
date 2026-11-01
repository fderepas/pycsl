r"""Test 7970 -- route #501 (control, expected PASS): a class K defines `index` / `format`; g calls them on a `K` parameter and on `K()`; f catches ValueError / KeyError around g; g returns 10, `ensures \result == 10`; CPython f() returns 10
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional

class K:
    def __init__(self) -> None:
        self.v = 0

    #@ ensures \result == x
    def index(self, x: int) -> int:
        return x

    #@ ensures \result == 0
    def format(self) -> int:
        return 0


#@ ensures \result == 10
def g(k: K) -> int:
    a = k.index(1)
    b = K().index(2)
    e = k.format()
    return 10


#@ ensures \result == 10
def f() -> int:
    try:
        return g(K())
    except ValueError:
        return 0
    except KeyError:
        return 0


if __name__ == "__main__":
    assert f() == 10
