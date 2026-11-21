r"""Test 4196 -- gen #37 route #322 (expected FAIL): `t = math.tau; t * 2 % 2 == 0` PROVED (CPython 0.566...). REFUSED now.
"""
# pycsl-expected: FAIL
import math
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    t = math.tau
    if t * 2 % 2 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 1, f()
