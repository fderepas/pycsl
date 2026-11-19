r"""Test 4350 -- gen #37 route #330 (expected FAIL): `z: complex` was typed `int`: `z * z == 0 or z * z != -1` PROVED (CPython False at 1j). A `complex` annotation is REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
#@ ensures \result == True
#@ assigns \nothing
def g(z: complex) -> bool:
    return z * z == 0 or z * z != -1

if __name__ == "__main__":
    assert g(complex(0, 1)) == True
