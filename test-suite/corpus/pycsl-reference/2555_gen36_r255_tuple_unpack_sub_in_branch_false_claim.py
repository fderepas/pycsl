r"""Test 2555 — route #255 (expected FAIL): tuple-unpack targets' arithmetic in a BRANCH (no flow into an
`int` slot): `a, b = x, x; if a - b == 0: return 1` PROVED `\result == 1`; now `a - b` is uninterpreted
and the claim FAILS. CPython: a user `__sub__` returns 7. PROVED at e6f26cde.
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures \result == 1
#@ assigns \nothing
def f(x: Any) -> int:
    a, b = x, x
    if a - b == 0:
        return 1
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
