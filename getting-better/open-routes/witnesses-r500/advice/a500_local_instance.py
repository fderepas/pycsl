r"""Test 7947 -- route #500 (control, expected PASS): the nested-return method called on a LOCAL instance uses its contract (no splice); CPython 11
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional


class C:
    def __init__(self) -> None:
        self.v: int = 0

    #@ ensures (n > 0) ==> \result == 1
    #@ ensures (n <= 0) ==> \result == 2
    #@ assigns \nothing
    def m(self, n: int) -> int:
        if n > 0:
            return 1
        return 2


#@ ensures \result == 11
def f(n: int) -> int:
    c = C()
    r = c.m(5)
    return r + 10


if __name__ == "__main__":
    assert f(0) == 11
