r"""Test 4343 -- gen #37 route #330 (expected FAIL): `self.r = 0.5` read as `self.r` in a method: `self.r % 1 == 0` PROVED. REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.r = 0.5

    #@ ensures \result == True
    #@ assigns \nothing
    def m(self) -> bool:
        return self.r * 2 == 2 * self.r and self.r % 1 == 0

if __name__ == "__main__":
    assert C().m() == True, C().m()
