r"""G29 GL8 — statement-position call on a module-global instance whose tail return divides by zero."""
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    def sget(self) -> int:
        return 1 // self.x


_g = C(0)


#@ ensures \result == 5
def probe() -> int:
    _g.sget()
    return 5


if __name__ == "__main__":
    print("CPython:", probe())
