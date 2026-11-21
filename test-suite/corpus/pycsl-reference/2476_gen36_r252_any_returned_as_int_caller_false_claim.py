r"""Test 2476 — route #252 (expected FAIL): the CALLER of an `-> int` function that returns its `Any`
argument used the result as an int: `y = h(x); return y - y` PROVED `\result == 0`. CPython: a user
`__sub__` returns 7. PROVED at 15f8c4bd; the `return` in `h` is now REFUSED fail-closed.
"""
# pycsl-expected: FAIL
from typing import Any


#@ assigns \nothing
def h(x: Any) -> int:
    return x


#@ ensures \result == 0
#@ assigns \nothing
def f(x: Any) -> int:
    y = h(x)
    return y - y


if __name__ == "__main__":
    class P:
        def __sub__(self, o: object) -> int:
            return 7

    assert f(P()) == 7
