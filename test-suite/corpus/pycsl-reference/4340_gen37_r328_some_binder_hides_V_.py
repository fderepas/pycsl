r"""Test 4340 -- gen #37 route #328 (expected FAIL): `| Some v_ -> v_` (a `d.get` lowering) hid a global `V_ = 0.5` declaration-wide: `V_ % 1 == 0` PROVED. REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
from typing import Dict
V_ = 0.5
#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    d: Dict[str, int] = {"a": 1}
    w = d.get("a")
    if V_ % 1 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert g() == 1, g()
