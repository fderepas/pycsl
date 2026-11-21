r"""Test 4830 -- gen #37 route #357: CONTROL: in a field-less class a `-> int` method result keeps the int laws (`v - v == 0`), and `type(self)()` / `self.__class__()` with no argument outside `no_exception` are admitted (their erased values unused); PROVES (CPython 0).
"""
# pycsl-expected: PASS
class W:
    def k(self) -> int:
        return 3

    #@ ensures \result == 0
    def m(self) -> int:
        v = self.k()
        o = type(self)()
        t = self.__class__()
        return v - v


if __name__ == "__main__":
    r = W().m()
    assert r == 0, r
