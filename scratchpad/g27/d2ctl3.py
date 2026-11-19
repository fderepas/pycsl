r"""D2-CTL3 — positive control: the `self.` receiver path, whose default fill DOES supply the
default, must keep its (correct) refusal — the default -1 makes `not (-1 < 0)` unprovable."""
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
