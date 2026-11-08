r"""G29 RQ8 — a violated param `requires` on a sibling self-call."""
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    #@ requires d != 0
    #@ ensures \result == 1
    def get(self, d: int) -> int:
        return d // d

    #@ ensures \result == 5
    def run(self) -> int:
        self.get(0)
        return 5


#@ ensures \result == 5
def probe() -> int:
    c = C(3)
    return c.run()


if __name__ == "__main__":
    print("CPython:", probe())
