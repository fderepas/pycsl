r"""G29 RQ6 — non-self requires violated, result discarded."""
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    #@ requires d != 0
    #@ ensures \result == 1
    def get(self, d: int) -> int:
        return d // d


#@ ensures \result == 5
def probe() -> int:
    c = C(3)
    c.get(0)
    return 5


if __name__ == "__main__":
    print("CPython:", probe())
