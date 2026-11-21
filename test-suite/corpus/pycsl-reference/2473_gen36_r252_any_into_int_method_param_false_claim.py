r"""Test 2473 — route #252 (expected FAIL): the method form `k.g(x, x)` of 2470 (an `int`-annotated
method parameter) PROVED `\result == 0` for `x: Any`. CPython: a user `__sub__` returns 7.
PROVED at 15f8c4bd; now REFUSED fail-closed.
"""
# pycsl-expected: FAIL
from typing import Any


class K:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result == a - b
    #@ assigns \nothing
    def g(self, a: int, b: int) -> int:
        return a - b


#@ ensures \result == 0
#@ assigns \nothing
def f(k: K, x: Any) -> int:
    return k.g(x, x)


if __name__ == "__main__":
    class P:
        def __sub__(self, o: object) -> int:
            return 7

    assert f(K(), P()) == 7
