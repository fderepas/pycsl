r"""Test 4613 -- gen #37 route #343 (expected FAIL): witness h03: `s = self; return s == s` with a user `__eq__` returning False; `ensures \result == True` PROVED (CPython False). FAIL (erased `==` is uninterpreted).
"""
# pycsl-expected: FAIL
class W:
    def __eq__(self, o: object) -> bool:
        return False
    #@ ensures \result == True
    def m(self) -> bool:
        s = self
        return s == s

if __name__ == "__main__":
    assert W().m() is False
