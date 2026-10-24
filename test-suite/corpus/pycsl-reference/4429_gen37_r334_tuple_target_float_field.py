r"""Test 4429 -- gen #37 route #334 (expected FAIL): a tuple-target field initialisation `self.r, self.s = 2.5, 1` escaped the classifier (and #315: the class is opaque, `c.r` an unconstrained getter) and `c.r % 1 == 0` PROVED (CPython False). REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK): tuple targets are paired element-wise.
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.r, self.s = 2.5, 1

#@ assigns \nothing
#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    c = C()
    return 1 if c.r % 1 == 0 else 0

if __name__ == "__main__":
    assert g() == 1, g()
