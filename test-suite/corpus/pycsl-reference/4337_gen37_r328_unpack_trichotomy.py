r"""Test 4337 -- gen #37 route #328 (expected FAIL): `e, _ = EPS, 0` then `x < e or x >= e + 1 or x == e` PROVED (#325 t06 re-opened through unpacking). REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
EPS = 0.5
#@ ensures \result == True
#@ assigns \nothing
def g(x: int) -> bool:
    e, _ = EPS, 0
    return x < e or x >= e + 1 or x == e

if __name__ == "__main__":
    assert g(1) == True, g(1)
