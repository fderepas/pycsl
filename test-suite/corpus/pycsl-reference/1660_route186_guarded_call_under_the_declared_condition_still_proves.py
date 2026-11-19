r"""Test 1660 - ROUTE #186 control (gen #29): the same field-receiver call with an argument the callee's `raises` condition excludes (v = 1) still proves under `#@ no_exception ValueError`.
"""
_ = 0  # anchor


class Inner:
    def __init__(self) -> None:
        self.k = 0

    #@ raises ValueError when v < 0
    def go(self, v: int) -> int:
        if v < 0:
            raise ValueError()
        return v


class Outer:
    def __init__(self) -> None:
        self.inner = Inner()

    #@ no_exception ValueError
    #@ ensures \result == 0
    def run(self) -> int:
        self.inner.go(1)
        return 0
