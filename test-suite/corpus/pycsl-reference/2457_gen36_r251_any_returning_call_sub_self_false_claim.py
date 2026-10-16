r"""Test 2457 — route #251 (expected FAIL): The result of a function declared `-> Any`: `return h(x) - h(x)` PROVED
`\result == 0`. CPython: `h` returns its argument, whose `__sub__` returns 7.
PROVED at aaf9b355.
"""
# pycsl-expected: FAIL
from typing import Any


#@ assigns \nothing
def h(v: Any) -> Any:
    return v


#@ ensures \result == 0
#@ assigns \nothing
def f(x: Any) -> int:
    return h(x) - h(x)


if __name__ == "__main__":
    class P:
        def __sub__(self, o: object) -> int:
            return 7

    assert f(P()) == 7
