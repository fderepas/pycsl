r"""Test 4357 -- gen #37 route #330 (expected PASS): control: an int field `self.n = 3` beside a float field keeps its model (and the method's frame `self.r = old self.r` is admitted): `self.n % 1 == 0` PROVES.
"""
# pycsl-expected: PASS
class C:
    def __init__(self) -> None:
        self.n = 3
        self.r = 0.5

    #@ ensures \result == True
    #@ assigns \nothing
    def m(self) -> bool:
        return self.n % 1 == 0

if __name__ == "__main__":
    assert C().m() == True
