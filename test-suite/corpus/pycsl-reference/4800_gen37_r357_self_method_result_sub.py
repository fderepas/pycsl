r"""Test 4800 -- gen #37 route #357 (expected FAIL): witness r01: `s = self.me()` (`-> "W"`, a field-less class) then `s - s` with a user `__sub__` returning 1; `ensures \result == 0` PROVED (CPython 1). REFUSED (route #252: the now-erased method result flows into `-> int`).
"""
# pycsl-expected: FAIL
class W:
    def __sub__(self, o: object) -> int:
        return 1

    def me(self) -> "W":
        return self

    #@ ensures \result == 0
    def m(self) -> int:
        s = self.me()
        return s - s


if __name__ == "__main__":
    r = W().m()
    assert r == 1, r
