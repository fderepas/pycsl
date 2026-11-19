r"""Test 2352 — route #248 (expected FAIL): the equality comes from the CONTRACT, the type tests from
the body: `requires x == y` forced the two program `str` tests equal and `\result == 1` PROVED at
afe28c69. CPython `f("s", W())` = 0.
"""
# pycsl-expected: FAIL
from typing import Any


#@ requires x == y
#@ ensures \result == 1
#@ assigns \nothing
def f(x: Any, y: Any) -> int:
    if isinstance(x, str):
        if not isinstance(y, str):
            return 0
    return 1


if __name__ == "__main__":
    class W:
        def __eq__(self, o: object) -> bool:
            return True

    assert "s" == W()
    assert f("s", W()) == 0
