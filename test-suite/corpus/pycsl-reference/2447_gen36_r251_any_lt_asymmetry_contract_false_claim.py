r"""Test 2447 — route #251 (expected FAIL): Contract side: `requires x < y` PROVED `ensures not (y < x)` on two `Any`
parameters. CPython: `__lt__ -> True`; both orders are True.
PROVED at aaf9b355.
"""
# pycsl-expected: FAIL
from typing import Any


#@ requires x < y
#@ ensures not (y < x)
#@ assigns \nothing
def f(x: Any, y: Any) -> int:
    return 0


if __name__ == "__main__":
    class P:
        def __lt__(self, o: object) -> bool:
            return True

    x, y = P(), P()
    assert (x < y) and (y < x)
