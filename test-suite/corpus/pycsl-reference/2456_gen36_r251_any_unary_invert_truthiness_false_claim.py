r"""Test 2456 — route #251 (expected FAIL): Unary `~` on `x: Any` was `(- x) - 1`, so `not x` (x = 0) decided `~x` truthy
and `if not x: if not ~x: return 1` was unreachable (`\result == 0` PROVED). CPython: `__bool__ -> False`, `__invert__
-> 0`.
PROVED at aaf9b355.
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures \result == 0
#@ assigns \nothing
def f(x: Any) -> int:
    if not x:
        if not ~x:
            return 1
    return 0


if __name__ == "__main__":
    class P:
        def __bool__(self) -> bool:
            return False

        def __invert__(self) -> int:
            return 0

    assert f(P()) == 1
