r"""G29 UX-Z3 — the method raises through a module function."""
_ = 0  # anchor


def check(v: int) -> None:
    if v < 0:
        raise ValueError()


class C:
    def __init__(self) -> None:
        self.k = 0

    def go(self, v: int) -> int:
        check(v)
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
