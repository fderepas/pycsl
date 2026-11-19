r"""Test 1417 — ROUTE #140 control: when the actual IS supplied the substitution is complete, the condition renders in terms of the caller\x27s actual, and the `no_exception` obligation is discharged exactly as before.
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
def caller(k: int) -> int:
    c = H()
    return c.f(k)