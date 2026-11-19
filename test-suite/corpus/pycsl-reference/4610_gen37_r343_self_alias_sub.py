r"""Test 4610 -- gen #37 route #343 (expected FAIL): witness b01: `s = self; return s - s` in a method of field-less `W` whose `__sub__` returns 1; `ensures \result == 0` PROVED (CPython 1). REFUSED (route #252: the erased receiver flows into `-> int`).
"""
# pycsl-expected: FAIL
class W:
    def __sub__(self, o: object) -> int:
        return 1
    #@ ensures \result == 0
    def m(self) -> int:
        s = self
        return s - s

if __name__ == "__main__":
    assert W().m() == 1, "CPython runs the user __sub__"
