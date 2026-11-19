r"""G29 DU-D8 — user DUNDER dispatch: __ne__ inconsistent (claim != truth; CPython 0)."""
_ = 0  # anchor


class C:
    def __init__(self, v: int) -> None:
        self.v = v
    def __ne__(self, other: object) -> bool:
        return False


#@ ensures \result != 0
def probe() -> int:
    a = C(1)
    b = C(2)
    return 1 if a != b else 0


if __name__ == "__main__":
    print("CPython:", probe())
