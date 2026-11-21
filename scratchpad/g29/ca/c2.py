r"""G29 CA-C2 — class-level attribute state: instance attr shadows class attr (claim != truth; CPython 0)."""
_ = 0  # anchor


class C:
    count = 0

    def __init__(self) -> None:
        self.v = 1


#@ ensures \result != 0
def probe() -> int:
    c = C()
    c.count = 5
    return C.count


if __name__ == "__main__":
    print("CPython:", probe())
