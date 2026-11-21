r"""Test 5050 -- gen #37 route #373 (expected FAIL): a def nested in a method returning a field-less `self` (`-> "W"`), `t = g(); t - t` with a user `__sub__` -> 1; the bare call lowered to the opaque int stub `g_0 ()` and `\result == 0` PROVED (CPython 1). REFUSED now (route #252 flow of the erased call result into `-> int`).
"""
# pycsl-expected: FAIL
class W:
    def __sub__(self, o: object) -> int:
        return 1

    #@ ensures \result == 0
    def m(self) -> int:
        def g() -> "W":
            return self
        t = g()
        return t - t

if __name__ == "__main__":
    assert W().m() == 0, W().m()
