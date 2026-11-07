r"""Test 4430 -- gen #37 route #334 (expected FAIL): an INTEGRAL float field `self.r = 3.0` was carried as the int 3 and `c.r * 10**17 + 1 != c.r * 10**17` PROVED (CPython: float rounding makes them equal). REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK): only a direct comparison of an integral float is admitted.
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.r = 3.0

#@ assigns \nothing
#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    c = C()
    return 1 if c.r * 10**17 + 1 != c.r * 10**17 else 0

if __name__ == "__main__":
    assert g() == 1, g()
