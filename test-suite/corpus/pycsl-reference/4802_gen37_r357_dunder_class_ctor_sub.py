r"""Test 4802 -- gen #37 route #357 (expected FAIL): witness r22: `t = self.__class__()` then `t - t`; PROVED (CPython 1). REFUSED (route #252: `e.__class__()` is erased).
"""
# pycsl-expected: FAIL
class W:
    def __sub__(self, o: object) -> int:
        return 1

    #@ ensures \result == 0
    def m(self) -> int:
        t = self.__class__()
        return t - t


if __name__ == "__main__":
    r = W().m()
    assert r == 1, r
