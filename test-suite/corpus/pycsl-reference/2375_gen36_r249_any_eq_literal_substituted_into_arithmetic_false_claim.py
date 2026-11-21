r"""Test 2375 — route #249 (expected FAIL): `requires x == 5` PROVED `ensures \result == 6` for `return x + 1`: `x == 5` was the Why3 equation
`x = 5`, substituted into the (int-modelled) addition. CPython: `__eq__ -> True`, `__add__ -> 0`.
PROVED at fded262c.
"""
# pycsl-expected: FAIL
from typing import Any


#@ requires x == 5
#@ ensures \result == 6
#@ assigns \nothing
def f(x: Any) -> int:
    return x + 1


if __name__ == "__main__":
    class P:
        def __eq__(self, o: object) -> bool:
            return True

        def __add__(self, o: object) -> int:
            return 0

    assert P() == 5 and f(P()) == 0
