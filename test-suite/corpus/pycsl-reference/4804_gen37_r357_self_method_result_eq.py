r"""Test 4804 -- gen #37 route #357 (expected FAIL): witness r40: `s = self.me()` then `s == s` with a user `__eq__` returning False; `ensures \result == True` PROVED (CPython False). FAIL (route #249: `==` on an erased value is uninterpreted).
"""
# pycsl-expected: FAIL
class W:
    def __eq__(self, o: object) -> bool:
        return False
    __hash__ = object.__hash__

    def me(self) -> "W":
        return self

    #@ ensures \result == True
    def m(self) -> bool:
        s = self.me()
        return s == s


if __name__ == "__main__":
    r = W().m()
    assert r == False, r
