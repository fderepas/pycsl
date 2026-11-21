r"""Test 4803 -- gen #37 route #357 (expected FAIL): witness r38: `s = self.me()` then `s < s` under `no_exception \all`, class without `__lt__`; PROVED (CPython TypeError). FAIL (PyCSL-R252 operator on an erased operand).
"""
# pycsl-expected: FAIL
class P:
    def me(self) -> "P":
        return self

    #@ no_exception \all
    def m(self) -> bool:
        s = self.me()
        return s < s


if __name__ == "__main__":
    try:
        P().m()
        assert False, "expected TypeError"
    except TypeError:
        pass
