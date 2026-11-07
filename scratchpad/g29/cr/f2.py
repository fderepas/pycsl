r"""G29 F2 — the same with an annotated float field."""
_ = 0  # anchor


class Cy:
    r: float

    def __init__(self) -> None:
        self.r = 2.5

    #@ requires True
    #@ ensures True
    def big(self) -> int:
        if self.r > 2.0:
            return 1
        return 0


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    c = Cy()
    return c.big()


if __name__ == "__main__":
    print("CPython:", probe())
