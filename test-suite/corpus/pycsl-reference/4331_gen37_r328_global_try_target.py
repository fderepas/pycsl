r"""Test 4331 -- gen #37 route #328 (expected FAIL): `try: A = math.pi except: A = 0` at module level: `A % 1 == 0` PROVED (the #322 case back through a `try` body). REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
import math
try:
    A = math.pi
except Exception:
    A = 0
#@ ensures \result == True
#@ assigns \nothing
def g() -> bool:
    return A % 1 == 0

if __name__ == "__main__":
    assert g() == True, g()
