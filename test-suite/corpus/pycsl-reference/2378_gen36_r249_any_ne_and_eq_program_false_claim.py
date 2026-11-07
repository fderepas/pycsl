r"""Test 2378 — route #249 (expected FAIL): Program side: `x != y and x == y` was decided False (`<>` is the negation of `=`), so `\result == 0`
PROVED. CPython: `__eq__` and `__ne__` both True, `f(N(), N())` = 1.
PROVED at fded262c.
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures \result == 0
#@ assigns \nothing
def f(x: Any, y: Any) -> int:
    if x != y and x == y:
        return 1
    return 0


if __name__ == "__main__":
    class N:
        def __eq__(self, o: object) -> bool:
            return True

        def __ne__(self, o: object) -> bool:
            return True

    assert f(N(), N()) == 1
