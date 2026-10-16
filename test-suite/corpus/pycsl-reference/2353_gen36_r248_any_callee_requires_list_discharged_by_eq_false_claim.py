r"""Test 2353 — route #248 (expected FAIL): why control 2332's `requires isinstance(x, list)` cannot keep
the value application. `g`'s `requires y == z` and `isinstance(y, list)` discharged `c`'s `requires
isinstance(z, list)`, and `c`'s postcondition made `\result == 1` PROVE at afe28c69. CPython
`g([], W())` = 0 (`[] == W()` is True, `W()` is not a list).
"""
# pycsl-expected: FAIL
from typing import Any


#@ requires isinstance(x, list)
#@ ensures \result == 1
#@ assigns \nothing
def c(x: Any) -> int:
    if isinstance(x, list):
        return 1
    return 0


#@ requires y == z
#@ requires isinstance(y, list)
#@ ensures \result == 1
#@ assigns \nothing
def g(y: Any, z: Any) -> int:
    return c(z)


if __name__ == "__main__":
    class W:
        def __eq__(self, o: object) -> bool:
            return True

    assert [] == W()
    assert g([], W()) == 0
