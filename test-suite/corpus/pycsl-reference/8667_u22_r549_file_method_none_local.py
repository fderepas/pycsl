r"""Test 8667 -- route #549 (expected FAIL: PROVED at base, REFUSED PYCSL-R549-NONE-ARGUMENT; red team 52 probe bq1214): `v = None; Q().m(v)` of a method `m(self, x: int)`; CPython f(1) raises TypeError (in Q.m)
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
    v = None
    return Q().m(v)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
