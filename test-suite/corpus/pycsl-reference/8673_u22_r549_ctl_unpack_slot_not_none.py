r"""Test 8673 -- route #549 (control, expected PASS): `a, b = nothing(), k; g(b)`: the unpacked slot passed is the int one; CPython returns 2
"""
# pycsl-expected: PASS
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
    a, b = nothing(), k
    return g(b)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
