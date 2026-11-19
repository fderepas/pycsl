r"""Test 4757 -- gen #37 route #354 (expected FAIL): IntFlag `~x` lowered `-x-1`: `x + ~x == -1` PROVED (CPython 3, `~A == B`). REFUSED now (IntFlag is not int-like, route #354).
"""
# pycsl-expected: FAIL
from enum import IntFlag

class F(IntFlag):
    A = 1
    B = 2

#@ ensures \result == -1
def f() -> int:
    x = F.A
    return x + ~x

if __name__ == "__main__":
    assert f() == -1, f()
