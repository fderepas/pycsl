r"""Test 4352 -- gen #37 route #331 (expected FAIL): `no_exception \all` over `c.r + 1 > c.r` with `self.r: Optional[int] = None` PROVED. REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
from typing import Optional
class C:
    def __init__(self) -> None:
        self.r: Optional[int] = None

#@ no_exception \all
#@ ensures \result == True
#@ assigns \nothing
def g() -> bool:
    c = C()
    return c.r + 1 > c.r

if __name__ == "__main__":
    assert g() == True, g()
