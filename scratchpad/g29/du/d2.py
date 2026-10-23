r"""G29 DU-D2 — user DUNDER dispatch: __len__ (claim != truth; CPython 7)."""
_ = 0  # anchor


class C:
    def __init__(self, v: int) -> None:
        self.v = v
    def __len__(self) -> int:
        return 7


#@ ensures \result != 7
def probe() -> int:
    c = C(1)
    return len(c)


if __name__ == "__main__":
    print("CPython:", probe())
