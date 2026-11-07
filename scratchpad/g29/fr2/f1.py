r"""G29 FR2-1 — a method declaring `assigns self.a` writes a nested record field self.inner.x."""
_ = 0  # anchor


class In:
    def __init__(self) -> None:
        self.x = 0


class C:
    def __init__(self) -> None:
        self.a = 0
        self.inner = In()

    #@ assigns self.a
    def poke(self) -> None:
        self.a = 1
        self.inner.x = 5

    #@ ensures \result == 0
    def run(self) -> int:
        b = self.inner.x
        self.poke()
        return self.inner.x - b


if __name__ == "__main__":
    print("CPython:", C().run())
