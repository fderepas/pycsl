r"""G29 ER-M1 — the constructor REBINDS a parameter before storing it."""
_ = 0  # anchor


class C:
    def __init__(self, k: int) -> None:
        k = k + 1
        self.x = k


#@ ensures \result == 6
#@ assigns \nothing
def probe() -> int:
    c = C(5)
    return c.x


if __name__ == "__main__":
    print("CPython:", probe())
