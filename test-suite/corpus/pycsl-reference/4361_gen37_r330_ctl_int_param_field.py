r"""Test 4361 -- gen #37 route #330 (expected PASS): control: a field initialised from an `int` parameter keeps its model: `c.k * 0 == 0` PROVES.
"""
# pycsl-expected: PASS
class C:
    def __init__(self, k: int) -> None:
        self.r = 0.5
        self.k = k

#@ ensures \result == True
#@ assigns \nothing
def g() -> bool:
    c = C(4)
    return c.k * 0 == 0

if __name__ == "__main__":
    assert g() == True
