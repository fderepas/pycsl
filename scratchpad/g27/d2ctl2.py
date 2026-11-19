r"""D2-CTL2 — positive control for the #140 repair: the SAME callee called with the argument
SUPPLIED must still verify (the substitution is complete)."""
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
def caller(k: int) -> int:
    c = H()
    return c.f(k)
