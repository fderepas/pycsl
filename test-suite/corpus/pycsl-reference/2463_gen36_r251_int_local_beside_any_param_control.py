r"""Test 2463 — route #251 (expected PASS): CONTROL: an `int` parameter next to an `Any` one keeps integer arithmetic: `s
= n + 1; return s - n` still PROVES `\result == 1` (true in CPython for every int `n`).
"""
# pycsl-expected: PASS
from typing import Any


#@ ensures \result == 1
#@ assigns \nothing
def f(x: Any, n: int) -> int:
    s = n + 1
    return s - n


if __name__ == "__main__":
    for n in range(-3, 4):
        assert f(object(), n) == 1
