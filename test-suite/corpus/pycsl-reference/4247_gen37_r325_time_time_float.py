r"""Test 4247 -- gen #37 route #325 (expected FAIL): `t = time.time(); t // 1 == t` PROVED through `val time_time_0 () : int` (CPython violates the contract). An opaque-int fallback of a non-int value; REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
import time
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    if time.time() % 1 == 0 or True:
        pass
    t = time.time()
    if t // 1 == t:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 1, f()
