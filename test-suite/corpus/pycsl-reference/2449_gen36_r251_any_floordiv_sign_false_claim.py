r"""Test 2449 — route #251 (expected FAIL): `requires x >= 0` PROVED `ensures \result >= 0` for `return x // 2` on `x:
Any` (integer `>=` and `div`). CPython: `__ge__ -> True`, `__floordiv__ -> -1`.
PROVED at aaf9b355.
"""
# pycsl-expected: FAIL
from typing import Any


#@ requires x >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def f(x: Any) -> int:
    return x // 2


if __name__ == "__main__":
    class P:
        def __ge__(self, o: object) -> bool:
            return True

        def __floordiv__(self, o: object) -> int:
            return -1

    x = P()
    assert x >= 0 and f(x) == -1
