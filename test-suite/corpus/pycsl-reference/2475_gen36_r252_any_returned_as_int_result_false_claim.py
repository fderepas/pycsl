r"""Test 2475 — route #252 (expected FAIL): `return x` (`x: Any`) from a function declared `-> int` made
`\result` an int, so `\result - \result == 0` PROVED. CPython: the result IS the argument, and a
user `__sub__` returns 7. PROVED at 15f8c4bd; now REFUSED fail-closed.
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures \result - \result == 0
#@ assigns \nothing
def h(x: Any) -> int:
    return x


if __name__ == "__main__":
    class P:
        def __sub__(self, o: object) -> int:
            return 7

    r = h(P())
    assert r - r == 7
