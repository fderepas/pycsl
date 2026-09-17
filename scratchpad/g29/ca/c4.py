r"""G29 CA-C4 — class-level attribute state: classmethod mutates cls attr (claim != truth; CPython 7)."""
_ = 0  # anchor


class C:
    count = 0

    def __init__(self) -> None:
        self.v = 1
    @classmethod
    def setc(cls, k: int) -> None:
        cls.count = k


#@ ensures \result != 7
def probe() -> int:
    C.setc(7)
    return C.count


if __name__ == "__main__":
    print("CPython:", probe())
