r"""G29 DU-D4 — user DUNDER dispatch: __contains__ (claim != truth; CPython 1)."""
_ = 0  # anchor


class C:
    def __init__(self, v: int) -> None:
        self.v = v
    def __contains__(self, x: int) -> bool:
        return True


#@ ensures \result != 1
def probe() -> int:
    c = C(1)
    return 1 if 5 in c else 0


if __name__ == "__main__":
    print("CPython:", probe())
