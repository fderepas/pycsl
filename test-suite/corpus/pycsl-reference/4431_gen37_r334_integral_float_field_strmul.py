r"""Test 4431 -- gen #37 route #334 (expected FAIL): an INTEGRAL float field `self.r = 2.0`, `no_exception` + `len("ab" * c.r) == 4` PROVED (CPython TypeError: a str times a float). REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.r = 2.0

#@ no_exception \all
#@ ensures \result == 4
#@ assigns \nothing
def g() -> int:
    c = C()
    return len("ab" * c.r)

if __name__ == "__main__":
    assert g() == 4, g()
