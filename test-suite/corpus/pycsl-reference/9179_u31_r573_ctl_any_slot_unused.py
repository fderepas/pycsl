r"""Test 9179 -- route #573 (control, expected PASS): a call returning `Tuple[Any, int]` / `Tuple[int, Any]` read only at its `int` slot (`t[1] + 1`, `t[0] + 1`) -- the `Any` slot is never used as a number; CPython 2 3
"""
# pycsl-expected: PASS
from typing import Any, Tuple


def g(k: int) -> Tuple[Any, int]:
    return (None, k)


def g2(k: int) -> Tuple[int, Any]:
    return (k, "x")


#@ no_exception \all
def f1(k: int) -> int:
    t = g(k)
    return t[1] + 1


#@ no_exception \all
def f2(k: int) -> int:
    t = g2(k)
    return t[0] + 1


if __name__ == "__main__":
    print(f1(1), f2(2))
