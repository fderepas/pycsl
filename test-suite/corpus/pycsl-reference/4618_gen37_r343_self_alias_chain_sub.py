r"""Test 4618 -- gen #37 route #343 (expected FAIL): witness h10: `t = self; u = t; return u - t` with a user `__sub__` returning 1; `ensures \result == 0` PROVED (CPython 1). REFUSED.
"""
# pycsl-expected: FAIL
class W:
    def __sub__(self, o: object) -> int:
        return 1
    #@ ensures \result == 0
    def m(self) -> int:
        t = self
        u = t
        return u - t

if __name__ == "__main__":
    assert W().m() == 1
