r"""Test 4323 -- gen #37 route #329 (expected FAIL): `0 if x is not True else 7` with `x = 1` PROVED 7 (CPython 0). REFUSED.
"""
# pycsl-expected: FAIL
#@ ensures \result == 7
#@ assigns \nothing
def g() -> int:
    x = 1
    return 0 if x is not True else 7

if __name__ == "__main__":
    assert g() == 7, g()
