r"""Test 1612 - ROUTE #176 (gen #29): the same through a sibling `self.go(-1)` PROVED `\result == 0` (CPython 9).
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.k = 0

    def go(self, v: int) -> int:
        if v < 0:
            raise ValueError()
        return v

    #@ ensures \result == 0
    def run(self) -> int:
        try:
            self.go(-1)
        except ValueError:
            return 9
        return 0
