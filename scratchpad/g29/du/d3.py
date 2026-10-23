r"""G29 DU-D3 — user DUNDER dispatch: __bool__ False (claim != truth; CPython 0)."""
_ = 0  # anchor


class C:
    def __init__(self, v: int) -> None:
        self.v = v
    def __bool__(self) -> bool:
        return False


#@ ensures \result != 0
def probe() -> int:
    c = C(1)
    return 1 if c else 0


if __name__ == "__main__":
    print("CPython:", probe())
