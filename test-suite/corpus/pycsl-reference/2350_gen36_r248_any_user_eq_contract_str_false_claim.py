r"""Test 2350 — route #248 (expected FAIL): `==` on `Any` values was read as BUILTIN equality, which
never crosses `str`; a user `__eq__` does. `requires x == y` PROVED `ensures isinstance(x, str) ==
isinstance(y, str)` at afe28c69. CPython: `x = W()` (`__eq__` always True), `y = "s"`.
"""
# pycsl-expected: FAIL
from typing import Any


#@ requires x == y
#@ ensures isinstance(x, str) == isinstance(y, str)
#@ assigns \nothing
def f(x: Any, y: Any) -> int:
    return 0


if __name__ == "__main__":
    class W:
        def __eq__(self, o: object) -> bool:
            return True

    assert W() == "s"
    assert isinstance(W(), str) != isinstance("s", str)
