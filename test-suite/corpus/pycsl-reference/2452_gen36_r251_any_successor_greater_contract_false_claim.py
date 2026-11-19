r"""Test 2452 — route #251 (expected FAIL): Contract arithmetic and ordering: `ensures x + 1 > x` on `x: Any` PROVED.
CPython: for `x = 2.0 ** 53`, `x + 1 == x` (binary64 rounding), so `x + 1 > x` is False.
PROVED at aaf9b355.
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures x + 1 > x
#@ assigns \nothing
def f(x: Any) -> int:
    return 0


if __name__ == "__main__":
    x = 2.0 ** 53
    assert not (x + 1 > x)
