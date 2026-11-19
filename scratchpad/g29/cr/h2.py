r"""G29 H2 — route #149: a positional default bound BY KEYWORD at the call site."""
_ = 0  # anchor


class Cy:
    def __init__(self, q: int = 1, r: int = 5) -> None:
        self.q = q
        self.r = r


#@ ensures \result == 5
#@ assigns \nothing
def probe() -> int:
    c = Cy(r=9)
    return c.r - c.q + 1 - 4
