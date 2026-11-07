r"""Test 2374 — route #249 (expected FAIL): `requires x == 5 and y == 5` PROVED `ensures x == y` (`x = 5`, `y = 5` in the model). CPython: a
class equal to the int 5 only (`isinstance(o, int) and o == 5`), two instances.
PROVED at fded262c.
"""
# pycsl-expected: FAIL
from typing import Any


#@ requires x == 5 and y == 5
#@ ensures x == y
#@ assigns \nothing
def f(x: Any, y: Any) -> int:
    return 0


if __name__ == "__main__":
    class F:
        def __eq__(self, o: object) -> bool:
            return isinstance(o, int) and o == 5

    x, y = F(), F()
    assert x == 5 and y == 5 and not (x == y)
