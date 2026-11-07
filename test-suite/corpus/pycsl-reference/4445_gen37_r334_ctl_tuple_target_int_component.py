r"""Test 4445 -- gen #37 route #334 (expected PASS): control: beside a float component of a tuple-target field initialisation (`self.r, self.s = 2.5, 1`, twin 4429), the INT component keeps its model (the opaque class's getter `get_s` of a provably-int field): `c.s % 1 == 0` PROVES.
"""
# pycsl-expected: PASS
class C:
    def __init__(self) -> None:
        self.r, self.s = 2.5, 1


#@ ensures \result == True
#@ assigns \nothing
def g() -> bool:
    c = C()
    return c.s % 1 == 0

if __name__ == "__main__":
    assert g() == True, g()
