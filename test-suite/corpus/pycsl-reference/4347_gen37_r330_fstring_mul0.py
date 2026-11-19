r"""Test 4347 -- gen #37 route #330 (expected FAIL): `f"{n}"` is the int `str_of_int_hash n`: `s * 0 == 0` PROVED. REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
#@ ensures \result == True
#@ assigns \nothing
def g(n: int) -> bool:
    s = f"{n}"
    return s * 0 == 0

if __name__ == "__main__":
    assert g(1) == True
