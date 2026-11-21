r"""G29 DU-D1 — user DUNDER dispatch: __eq__ always True (claim != truth; CPython 1)."""
_ = 0  # anchor


class C:
    def __init__(self, v: int) -> None:
        self.v = v
    def __eq__(self, other: object) -> bool:
        return True


#@ ensures \result != 1
def probe() -> int:
    a = C(1)
    b = C(2)
    return 1 if a == b else 0


if __name__ == "__main__":
    print("CPython:", probe())
