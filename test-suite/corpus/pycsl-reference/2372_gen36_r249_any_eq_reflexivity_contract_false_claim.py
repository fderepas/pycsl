r"""Test 2372 — route #249 (expected FAIL): `ensures x == x` PROVED on an `Any` parameter (Why3 `=` is reflexive). CPython: `x = float("nan")`
(no user class needed), or any `__eq__` returning False.
PROVED at fded262c.
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures x == x
#@ assigns \nothing
def f(x: Any) -> int:
    return 0


if __name__ == "__main__":
    x = float("nan")
    assert not (x == x)
