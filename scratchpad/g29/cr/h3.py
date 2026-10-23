r"""G29 H3 — route #149 draft: a NEGATIVE positional default spliced into an expression."""
_ = 0  # anchor


class Cy:
    def __init__(self, r: int = -5) -> None:
        self.r = r * 2


#@ ensures \result == -10
#@ assigns \nothing
def probe() -> int:
    c = Cy()
    return c.r
