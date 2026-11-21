r"""Test 4338 -- gen #37 route #328 (expected FAIL): the emitter's `with Return r -> r` binder was scoped to the whole declaration and hid a global `R = 0.5`: `R % 1 == 0` PROVED. REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
R = 0.5
#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    if R % 1 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert g() == 1, g()
