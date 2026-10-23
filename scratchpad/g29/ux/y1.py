r"""G29 UX-Y1 — a method raising ValueError, caught by the caller."""
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.k = 0

    def go(self, v: int) -> int:
        if v < 0:
            raise ValueError()
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
