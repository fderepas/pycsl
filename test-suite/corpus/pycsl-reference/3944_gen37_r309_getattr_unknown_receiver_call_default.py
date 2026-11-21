r"""Test 3944 -- gen #37 route #309 (expected FAIL): `getattr(a, "n", z())` on `Any` receivers: one shared constant; now REFUSED.
"""
# pycsl-expected: FAIL
from typing import Any

#@ ensures \result == 0
def z() -> int:
    return 0

#@ ensures \result == 0
def f(a: Any, b: Any) -> int:
    v = getattr(a, "n", z())
    w = getattr(b, "n", z())
    if v == w:
        return 0
    return 1

class K:
    def __init__(self, v: int) -> None:
        self.n = v

if __name__ == "__main__":
    assert f(K(4), K(5)) == 0
