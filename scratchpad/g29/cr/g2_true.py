r"""G29 G2 — route #82's constant capture excludes `bool`: an omitted keyword-only `True` default."""
_ = 0  # anchor


class Cy:
    def __init__(self, *, r: int = True) -> None:
        self.r = r


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    c = Cy()
    if c.r > 0:
        return 1
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
