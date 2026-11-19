r"""G29 DU-D5 — user DUNDER dispatch: __getitem__ (claim != truth; CPython 42)."""
_ = 0  # anchor


class C:
    def __init__(self, v: int) -> None:
        self.v = v
    def __getitem__(self, i: int) -> int:
        return 42


#@ ensures \result != 42
def probe() -> int:
    c = C(1)
    return c[0]


if __name__ == "__main__":
    print("CPython:", probe())
