r"""Test 2451 — route #251 (expected FAIL): An element of a `List[Any]`: `return xs[0] - xs[0]` PROVED `\result == 0`.
CPython: a user `__sub__` returns 7.
PROVED at aaf9b355.
"""
# pycsl-expected: FAIL
from typing import Any, List


#@ requires len(xs) >= 1
#@ ensures \result == 0
#@ assigns \nothing
def f(xs: List[Any]) -> int:
    return xs[0] - xs[0]


if __name__ == "__main__":
    class P:
        def __sub__(self, o: object) -> int:
            return 7

    assert f([P()]) == 7
