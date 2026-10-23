r"""Test 1418 — ROUTE #140 control: the `self.` receiver path already filled defaults before the wrap, so its substitution was complete and its verdict is unchanged.
"""
_ = 0  # anchor


class H:
    tag: int

    def __init__(self) -> None:
        self.tag = 0

    #@ raises ValueError when k < 0
    #@ assigns \nothing
    def f(self, k: int = -1) -> int:
        m = k
        if m < 0:
            raise ValueError
        return m

    #@ requires k >= 0
    #@ assigns \nothing
    #@ no_exception ValueError
    def caller(self, k: int) -> int:
        return self.f(k)