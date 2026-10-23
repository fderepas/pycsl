r"""G29 CA-C3 — class-level attribute state: class attr read through instance after class store (claim != truth; CPython 3)."""
_ = 0  # anchor


class C:
    count = 0

    def __init__(self) -> None:
        self.v = 1


#@ ensures \result != 3
def probe() -> int:
    C.count = 3
    c = C()
    return c.count


if __name__ == "__main__":
    print("CPython:", probe())
