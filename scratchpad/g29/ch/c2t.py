r"""G29 CH2 — chained assignment to a FIELD as the second target."""
_ = 0  # anchor


class Cy:
    def __init__(self) -> None:
        self.r = 1


#@ ensures \result == 5
def f() -> int:
    c = Cy()
    a = c.r = 5
    return c.r


if __name__ == "__main__":
    print("CPython:", f())
