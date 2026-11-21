r"""G29 RQ4 — a violated method `requires` whose result is discarded."""
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    #@ requires self.x != 0
    #@ ensures \result == 1
    def get(self) -> int:
        return self.x // self.x


#@ ensures \result == 5
def probe() -> int:
    c = C(0)
    c.get()
    return 5


if __name__ == "__main__":
    print("CPython:", probe())
