r"""G29 H4F — route #149: a negative default under floor division (Python floors: -5 // 2 == -3)."""
_ = 0  # anchor


class Cy:
    def __init__(self, r: int = -5) -> None:
        self.r = r // 2


#@ ensures \result == -2
#@ assigns \nothing
def probe() -> int:
    c = Cy()
    return c.r
