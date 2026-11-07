r"""Test 2440 — route #251 (expected FAIL): `return x - x` on `x: Any` PROVED `\result == 0`: `-` on an erased value was
Why3 integer subtraction. CPython: a user `__sub__` returns 7.
PROVED at aaf9b355.
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures \result == 0
#@ assigns \nothing
def f(x: Any) -> int:
    return x - x


if __name__ == "__main__":
    class P:
        def __sub__(self, o: object) -> int:
            return 7

    assert f(P()) == 7
