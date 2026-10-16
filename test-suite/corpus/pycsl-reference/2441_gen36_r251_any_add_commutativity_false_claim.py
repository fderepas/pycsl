r"""Test 2441 — route #251 (expected FAIL): `return (x + y) - (y + x)` on two `Any` parameters PROVED `\result == 0`
(commutativity of integer `+`). CPython: `A.__add__ -> 1`, `B.__add__ -> 2`; the result is -1.
PROVED at aaf9b355.
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures \result == 0
#@ assigns \nothing
def f(x: Any, y: Any) -> int:
    return (x + y) - (y + x)


if __name__ == "__main__":
    class A:
        def __add__(self, o: object) -> int:
            return 1

    class B:
        def __add__(self, o: object) -> int:
            return 2

    assert f(A(), B()) == -1
