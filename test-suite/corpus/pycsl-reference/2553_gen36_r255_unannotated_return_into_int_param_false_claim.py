r"""Test 2553 — route #255 (expected FAIL): the result of an unannotated-return `h`, passed to `g(a: int, b: int)`, bypassed route #252:
`v = h(x); return g(v, v)` PROVED `\result == 0`.
CPython: a user `__sub__` returns 7. PROVED at e6f26cde; now REFUSED fail-closed (route #252's flow refusal, now reached).
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures \result == a - b
#@ assigns \nothing
def g(a: int, b: int) -> int:
    return a - b


def h(y):
    return y


#@ ensures \result == 0
#@ assigns \nothing
def f(x: Any) -> int:
    v = h(x)
    return g(v, v)

if __name__ == "__main__":
    class S:
        def __sub__(self, o: object) -> int:
            return 7

        def __abs__(self) -> "S":
            return self

        def __gt__(self, o: object) -> bool:
            return False

        def __lt__(self, o: object) -> bool:
            return False

        def __getattr__(self, n: str) -> "S":
            return self

    print(f(S()))
