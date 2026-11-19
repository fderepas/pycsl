r"""Test 2448 — route #251 (expected FAIL): Unary minus: `-x` on `x: Any` was integer negation, so `bool(-x) == bool(x)`
was free and `if x: if not -x: return 1` was decided unreachable (`\result == 0` PROVED). CPython: `__bool__ -> True`,
`__neg__ -> 0`.
PROVED at aaf9b355.
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures \result == 0
#@ assigns \nothing
def f(x: Any) -> int:
    if x:
        if not -x:
            return 1
    return 0


if __name__ == "__main__":
    class P:
        def __bool__(self) -> bool:
            return True

        def __neg__(self) -> int:
            return 0

    assert f(P()) == 1
