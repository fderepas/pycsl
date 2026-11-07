r"""Test 4301 -- gen #37 route #327 (expected FAIL): `Y = n; y = 0; return Y`: `Y` and `y` fold together and `\result == 0` PROVED (CPython returns n). REFUSED.
"""
# pycsl-expected: FAIL
#@ requires n > 0
#@ ensures \result == 0
#@ assigns \nothing
def g(n: int) -> int:
    Y = n
    y = 0
    return Y

if __name__ == "__main__":
    assert g(2) == 0, g(2)
