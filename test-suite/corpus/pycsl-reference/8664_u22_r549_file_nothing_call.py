r"""Test 8664 -- route #549 (expected FAIL: PROVED at base, REFUSED PYCSL-R549-NONE-ARGUMENT; red team 52 probe bq1200): `g(nothing())` of a file `def g(x: int)` and `def nothing() -> None`; CPython f(1) raises TypeError (in g)
"""
# pycsl-expected: FAIL
from typing import Optional


def nothing() -> None:
    return None


def g(x: int) -> int:
    return x + 1


class Q:
    def __init__(self) -> None:
        self.a = 1

    def m(self, x: int) -> int:
        return x * 2


#@ no_exception \all
def f(k: int) -> int:
    return g(nothing())


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
