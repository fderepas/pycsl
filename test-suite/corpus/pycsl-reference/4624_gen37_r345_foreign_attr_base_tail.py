r"""Test 4624 -- gen #37 route #345 (expected FAIL): witness f01 (stdlib form): `import fractions as om; class S(om.Fraction)` while this file defines its own `class Fraction` with `ensures \result == 1` on `limit_denominator`; S inherited the LOCAL contract and `g(s) == 1` PROVED (CPython `S().limit_denominator()` is `Fraction(0, 1)`). REFUSED (PYCSL-R341-CLASS-BASE-NOT-A-NAME, route #345: a foreign attribute base whose tail names a class of the file).
"""
# pycsl-expected: FAIL
import fractions as om

class Fraction:
    def __init__(self) -> None:
        self.n = 1
    #@ ensures \result == 1
    def limit_denominator(self) -> int:
        return 1

class S(om.Fraction):
    pass

#@ ensures \result == 1
def g(s: S) -> int:
    return s.limit_denominator()

if __name__ == "__main__":
    assert g(S()) == 0, "CPython runs fractions.Fraction.limit_denominator"
