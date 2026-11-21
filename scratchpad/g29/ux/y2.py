r"""G29 UX-Y2 — a self-method raising ValueError, caught by a sibling method."""
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.k = 0

    def go(self, v: int) -> int:
        if v < 0:
            raise ValueError()
        return v

    #@ ensures \result == 0
    def run(self) -> int:
        try:
            self.go(-1)
        except ValueError:
            return 9
        return 0


if __name__ == "__main__":
    print("CPython:", C().run())
