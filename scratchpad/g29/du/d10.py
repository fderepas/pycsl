r"""G29 DU-D10 — user DUNDER dispatch: __neg__ (claim != truth; CPython 3)."""
_ = 0  # anchor


class C:
    def __init__(self, v: int) -> None:
        self.v = v
    def __neg__(self) -> int:
        return 3


#@ ensures \result != 3
def probe() -> int:
    c = C(1)
    return -c


if __name__ == "__main__":
    print("CPython:", probe())
