r"""G29 F3 — #139 float carrier, direct field read in the caller."""
_ = 0  # anchor


class Cy:
    def __init__(self) -> None:
        self.r = 2.5


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    c = Cy()
    if c.r > 2:
        return 1
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
