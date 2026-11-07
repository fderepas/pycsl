r"""Test 4426 -- gen #37 route #334 (expected FAIL): a str field through a local, `no_exception` + `c.s - c.s == 0` PROVED (CPython TypeError). REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        x = "ab"
        self.s = x

#@ no_exception \all
#@ ensures \result == 0
#@ assigns \nothing
def g() -> int:
    c = C()
    return c.s - c.s

if __name__ == "__main__":
    assert g() == 0, g()
