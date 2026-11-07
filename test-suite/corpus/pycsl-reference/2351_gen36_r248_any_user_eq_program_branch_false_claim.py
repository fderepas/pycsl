r"""Test 2351 — route #248 (expected FAIL): the program-side form. Under `if x == y` the two `str` tests
(`(typeof_op x) = 1`, `(typeof_op y) = 1`) were forced equal, so `\result == 1` PROVED at afe28c69.
CPython `f("s", W())` = 0 (`"s" == W()` falls back to `W.__eq__`).
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures \result == 1
#@ assigns \nothing
def f(x: Any, y: Any) -> int:
    if x == y:
        if isinstance(x, str):
            if not isinstance(y, str):
                return 0
    return 1


if __name__ == "__main__":
    class W:
        def __eq__(self, o: object) -> bool:
            return True

    assert f("s", W()) == 0
