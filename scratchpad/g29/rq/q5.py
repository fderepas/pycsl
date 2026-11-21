r"""G29 RQ5 — same with a parameter receiver."""
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    #@ requires self.x != 0
    #@ ensures \result == 1
    def get(self) -> int:
        return self.x // self.x


#@ ensures \result == 5
def use(c: C) -> int:
    c.get()
    return 5


#@ ensures \result == 5
def probe() -> int:
    return use(C(0))


if __name__ == "__main__":
    print("CPython:", probe())
