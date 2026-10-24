r"""Test 4346 -- gen #37 route #330 (expected FAIL): `repr(n)` is the int `repr_conv n`: `repr(n) * 0 == 0` PROVED (CPython `"" == 0` is False). REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
#@ ensures \result == True
#@ assigns \nothing
def g(n: int) -> bool:
    s = repr(n)
    return s * 0 == 0

if __name__ == "__main__":
    assert g(1) == True
