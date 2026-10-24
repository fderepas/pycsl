r"""Test 4634 -- gen #37 route #345: CONTROL: `import fractions as om; class S(om.Fraction)` while no class of the file is named `Fraction` (the local class is `Frac`): the base stays an imported base; PROVES (CPython 1).
"""
# pycsl-expected: PASS
import fractions as om

class Frac:
    def __init__(self) -> None:
        self.n = 1
    #@ ensures \result == 1
    def m(self) -> int:
        return 1

class S(om.Fraction):
    pass

#@ ensures \result == 1
def g(s: Frac) -> int:
    return s.m()

if __name__ == "__main__":
    assert g(Frac()) == 1
    assert S() == 0
