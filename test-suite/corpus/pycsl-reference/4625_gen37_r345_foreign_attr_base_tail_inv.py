r"""Test 4625 -- gen #37 route #345 (expected FAIL): witness f02 (stdlib form): as 4624 with a class invariant on the local `Fraction` and an own method on S; S inherited the local invariant and contract, `g(s) == 1` PROVED (CPython 0). REFUSED (PYCSL-R341-CLASS-BASE-NOT-A-NAME, route #345).
"""
# pycsl-expected: FAIL
import fractions as om

#@ class invariant self.n >= 0
class Fraction:
    def __init__(self) -> None:
        self.n = 1
    #@ ensures \result == 1
    def limit_denominator(self) -> int:
        return 1

class S(om.Fraction):
    def k(self) -> int:
        return 0

#@ ensures \result == 1
def g(s: S) -> int:
    return s.limit_denominator()

if __name__ == "__main__":
    assert g(S()) == 0
