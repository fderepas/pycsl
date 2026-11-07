r"""Test 4353 -- gen #37 route #331 (expected FAIL): `no_exception \all` over `c.s - c.s` with `self.s = "ab"` PROVED. REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.s = "ab"

#@ no_exception \all
#@ ensures \result == 0
#@ assigns \nothing
def g() -> int:
    c = C()
    return c.s - c.s

if __name__ == "__main__":
    assert g() == 0, g()
