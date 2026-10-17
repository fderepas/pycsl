r"""Test 2550 — route #255 (expected FAIL): a WALRUS target bound from an `Any` parameter was not erased: `if (v := x) is not None: return v - v`
PROVED `\result == 0`.
CPython: a user `__sub__` returns 7. PROVED at e6f26cde; now REFUSED fail-closed (route #252's flow refusal, now reached).
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures \result == 0
#@ assigns \nothing
def f(x: Any) -> int:
    if (v := x) is not None:
        return v - v
    return 0

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
