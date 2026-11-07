r"""G29 UX-Z2 — the method raises through a helper method."""
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.k = 0

    def check(self, v: int) -> None:
        if v < 0:
            raise ValueError()

    def go(self, v: int) -> int:
        self.check(v)
        return v


#@ ensures \result == 0
def probe() -> int:
    c = C()
    try:
        c.go(-1)
    except ValueError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
