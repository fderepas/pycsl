r"""G29 UX-X10 — a method raising a user subclass caught by a builtin base in the caller."""
_ = 0  # anchor


class MyErr(ValueError):
    pass


class C:
    def __init__(self) -> None:
        self.k = 0

    def go(self) -> int:
        raise MyErr()


#@ ensures \result == 0
def probe() -> int:
    c = C()
    try:
        c.go()
    except ValueError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
