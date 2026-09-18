r"""Test 1656 - ROUTE #185 (gen #29): a raising `Inner.go` called as `self.inner.go(-1)` inside `try ... except ValueError: return 9` PROVED `\result == 0` (CPython 9) - the same mis-keyed receiver, on route #176's may-raise prefix.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class Inner:
    def __init__(self) -> None:
        self.k = 0

    def go(self, v: int) -> int:
        if v < 0:
            raise ValueError()
        return v


class Outer:
    def __init__(self) -> None:
        self.inner = Inner()

    #@ ensures \result == 0
    def run(self) -> int:
        try:
            v = self.inner.go(-1)
        except ValueError:
            return 9
        return v * 0
