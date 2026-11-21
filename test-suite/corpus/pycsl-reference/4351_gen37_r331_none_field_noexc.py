r"""Test 4351 -- gen #37 route #331 (expected FAIL): `no_exception \all` over `c.r * 0` with `self.r = None` (record `{ r = pycsl_none }`) PROVED no exception (CPython TypeError). REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.r = None

#@ no_exception \all
#@ ensures \result == 0
#@ assigns \nothing
def g() -> int:
    c = C()
    return c.r * 0

if __name__ == "__main__":
    assert g() == 0, g()
