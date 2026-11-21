r"""G2 — carrier of MY OWN #139 repair: a FLOAT constant is captured by the existing arm as
`int(rhs.value)`, i.e. TRUNCATED to a definite wrong value."""
_ = 0  # anchor


class C:
    r: float

    def __init__(self) -> None:
        self.r = 2.5


#@ ensures \result == 2.0
#@ assigns \nothing
def probe() -> float:
    c = C()
    return c.r
