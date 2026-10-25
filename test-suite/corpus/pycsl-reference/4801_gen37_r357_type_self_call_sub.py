r"""Test 4801 -- gen #37 route #357 (expected FAIL): witness r15: `t = type(self)()` then `t - t` (user `__sub__` -> 1); PROVED (CPython 1). REFUSED (route #252: the erased `UnknownPyExpr` value flows into `-> int`).
"""
# pycsl-expected: FAIL
class W:
    def __sub__(self, o: object) -> int:
        return 1

    #@ ensures \result == 0
    def m(self) -> int:
        t = type(self)()
        return t - t


if __name__ == "__main__":
    r = W().m()
    assert r == 1, r
