r"""Test 4441 -- gen #37 route #334 (expected PASS): control: an INTEGRAL float field (`self.r = 3.0`) keeps its int model as a DIRECT operand of a comparison (CPython compares an int and a float exactly): `c.r > 1 and c.r == 3 and not (c.r < 0)` PROVES (routes #148 / #236: 1490). Arithmetic on it (4430, 4431) is refused.
"""
# pycsl-expected: PASS
class C:
    def __init__(self) -> None:
        self.r = 3.0


#@ ensures \result == True
#@ assigns \nothing
def g() -> bool:
    c = C()
    return c.r > 1 and c.r == 3 and not (c.r < 0)

if __name__ == "__main__":
    assert g() == True, g()
