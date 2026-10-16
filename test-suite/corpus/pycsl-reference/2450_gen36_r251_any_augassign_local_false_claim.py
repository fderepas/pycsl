r"""Test 2450 — route #251 (expected FAIL): Through a local: `y = x; y += 1; return y - (x + 1)` on `x: Any` PROVED
`\result == 0`. CPython: `y += 1` calls `__iadd__` (10), `x + 1` calls `__add__` (5); the result is 5.
PROVED at aaf9b355.
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures \result == 0
#@ assigns \nothing
def f(x: Any) -> int:
    y = x
    y += 1
    return y - (x + 1)


if __name__ == "__main__":
    class P:
        def __iadd__(self, o: object) -> int:
            return 10

        def __add__(self, o: object) -> int:
            return 5

    assert f(P()) == 5
