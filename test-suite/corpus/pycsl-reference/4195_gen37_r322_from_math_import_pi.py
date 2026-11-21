r"""Test 4195 -- gen #37 route #322 (expected FAIL): `from math import pi`; `pi % 1 == 0` PROVED (opaque `val constant pi : int`). REFUSED now.
"""
# pycsl-expected: FAIL
from math import pi
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    if pi % 1 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 1, f()
