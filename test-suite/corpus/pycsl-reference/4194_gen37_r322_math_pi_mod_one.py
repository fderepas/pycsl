r"""Test 4194 -- gen #37 route #322 (expected FAIL): `math.pi % 1 == 0` PROVED through the opaque int getter `get_pi` (CPython 0.14159...). REFUSED now.
"""
# pycsl-expected: FAIL
import math
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    if math.pi % 1 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 1, f()
