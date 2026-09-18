r"""G29 RQ1 — a method `requires` on self is violated by a caller holding a local instance."""
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    #@ requires self.x != 0
    #@ ensures \result == 1
    def get(self) -> int:
        return self.x // self.x


#@ ensures \result == 1
def probe() -> int:
    c = C(0)
    return c.get()


if __name__ == "__main__":
    print("CPython:", probe())
