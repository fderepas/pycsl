r"""G29 DU-D7 — user DUNDER dispatch: __lt__ via max (claim != truth; CPython 1)."""
_ = 0  # anchor


class C:
    def __init__(self, v: int) -> None:
        self.v = v
    def __lt__(self, other: 'C') -> bool:
        return self.v > other.v


#@ ensures \result != 1
def probe() -> int:
    a = C(1)
    b = C(2)
    return max(a, b).v


if __name__ == "__main__":
    print("CPython:", probe())
