r"""Test 2472 — route #252 (expected FAIL): the keyword form `g(a=x, b=x)` of 2470 PROVED `\result == 0`
for `x: Any`. CPython: a user `__sub__` returns 7. PROVED at 15f8c4bd; now REFUSED fail-closed.
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures \result == a - b
#@ assigns \nothing
def g(a: int, b: int) -> int:
    return a - b


#@ ensures \result == 0
#@ assigns \nothing
def f(x: Any) -> int:
    return g(a=x, b=x)


if __name__ == "__main__":
    class P:
        def __sub__(self, o: object) -> int:
            return 7

    assert f(P()) == 7
