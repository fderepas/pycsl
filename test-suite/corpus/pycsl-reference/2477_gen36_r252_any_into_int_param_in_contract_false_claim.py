r"""Test 2477 — route #252 (expected FAIL): in a CONTRACT, `g(x, x)` with `x: Any` applied `g`'s int
logic and PROVED `g(x, x) == 0`. CPython: `g(P(), P())` is 7. PROVED at 15f8c4bd; now REFUSED
fail-closed.
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures \result == a - b
#@ assigns \nothing
def g(a: int, b: int) -> int:
    return a - b


#@ ensures g(x, x) == 0
#@ assigns \nothing
def f(x: Any) -> int:
    return 0


if __name__ == "__main__":
    class P:
        def __sub__(self, o: object) -> int:
            return 7

    assert g(P(), P()) == 7
