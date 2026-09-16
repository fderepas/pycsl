r"""G29 DU-D9 — user DUNDER dispatch: __int__ (claim != truth; CPython 5)."""
_ = 0  # anchor


class C:
    def __init__(self, v: int) -> None:
        self.v = v
    def __int__(self) -> int:
        return 5


#@ ensures \result != 5
def probe() -> int:
    c = C(1)
    return int(c)


if __name__ == "__main__":
    print("CPython:", probe())
