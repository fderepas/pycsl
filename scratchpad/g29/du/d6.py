r"""G29 DU-D6 — user DUNDER dispatch: __add__ (claim != truth; CPython 99)."""
_ = 0  # anchor


class C:
    def __init__(self, v: int) -> None:
        self.v = v
    def __add__(self, other: 'C') -> int:
        return 99


#@ ensures \result != 99
def probe() -> int:
    a = C(1)
    b = C(2)
    return a + b


if __name__ == "__main__":
    print("CPython:", probe())
