r"""Test 4235 -- gen #37 route #325 (expected FAIL): module-level `M = math; M.pi % 1 == 0` (#322 bypass F1) PROVED (CPython violates the contract). An opaque-int fallback of a non-int value; REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
import math
M = math
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    if M.pi % 1 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 1, f()
