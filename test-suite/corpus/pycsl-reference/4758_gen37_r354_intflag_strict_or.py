r"""Test 4758 -- gen #37 route #354 (expected FAIL): `class F(IntFlag, boundary=STRICT)`: `x | 4` under `no_exception \all` PROVED (CPython ValueError). REFUSED now (route #354).
"""
# pycsl-expected: FAIL
from enum import IntFlag, STRICT

class F(IntFlag, boundary=STRICT):
    A = 1
    B = 2

#@ no_exception \all
def f() -> int:
    x = F.A
    y = x | 4
    return 0

if __name__ == "__main__":
    f()
