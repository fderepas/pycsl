r"""Test 2557 — route #255 (expected FAIL): the result of a call of `def h(z: T) -> T` (a TypeVar return) on an `Any` value was an `int`:
`return h(x) - h(x)` PROVED `\result == 0`.
CPython: a user `__sub__` returns 7. PROVED at e6f26cde; now REFUSED fail-closed (route #252's flow refusal, now reached).
"""
# pycsl-expected: FAIL
from typing import Any, TypeVar


T = TypeVar("T")


def h(z: T) -> T:
    return z


#@ ensures \result == 0
#@ assigns \nothing
def f(x: Any) -> int:
    return h(x) - h(x)

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
