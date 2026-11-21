r"""Test 4760 -- gen #37 route #354 (expected FAIL): NEW latent: `class F(int, Flag)` was int-like by its `int` base: `x + ~x == -1` PROVED (CPython 3). REFUSED now (route #354).
"""
# pycsl-expected: FAIL
from enum import Flag

class F(int, Flag):
    A = 1
    B = 2

#@ ensures \result == -1
def f() -> int:
    x = F.A
    return x + ~x

if __name__ == "__main__":
    assert f() == -1, f()
