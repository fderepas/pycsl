r"""Test 4322 -- gen #37 route #329 (expected FAIL): `elif not (x is not True): return 7` with `x = 1` PROVED `\result == 7` (CPython 0). REFUSED.
"""
# pycsl-expected: FAIL
#@ ensures \result == 7
#@ assigns \nothing
def g() -> int:
    x = 1
    if x == 5:
        return 3
    elif not (x is not True):
        return 7
    return 0

if __name__ == "__main__":
    assert g() == 7, g()
