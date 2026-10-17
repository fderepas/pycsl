r"""Test 2562 — route #255 (expected FAIL): `getattr` on an `Any` value returned an `int` (a user `__getattr__` runs):
`v = getattr(x, "a"); return v - v` PROVED `\result == 0`.
CPython: a user `__sub__` returns 7. PROVED at e6f26cde; now REFUSED fail-closed (route #252's flow refusal, now reached).
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures \result == 0
#@ assigns \nothing
def f(x: Any) -> int:
    v = getattr(x, "a")
    return v - v

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
