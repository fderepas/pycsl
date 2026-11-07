r"""Test 2443 — route #251 (expected FAIL): `return x * 0` on `x: Any` PROVED `\result == 0`. CPython: a user `__mul__`
returns 7.
PROVED at aaf9b355.
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures \result == 0
#@ assigns \nothing
def f(x: Any) -> int:
    return x * 0


if __name__ == "__main__":
    class P:
        def __mul__(self, o: object) -> int:
            return 7

    assert f(P()) == 7
