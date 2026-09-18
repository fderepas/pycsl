r"""G29 RQ2 — same, instance received as a parameter."""
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    #@ requires self.x != 0
    #@ ensures \result == 1
    def get(self) -> int:
        return self.x // self.x


#@ ensures \result == 1
def use(c: C) -> int:
    return c.get()


#@ ensures \result == 1
def probe() -> int:
    return use(C(0))


if __name__ == "__main__":
    print("CPython:", probe())
