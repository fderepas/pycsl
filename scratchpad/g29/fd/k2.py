r"""G29 FD2 — a METHOD keyword-only default, omitted."""
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.n = 1

    #@ ensures \result == k
    def m(self, *, k: int = 5) -> int:
        return k


#@ ensures \result == 0
def probe() -> int:
    c = C()
    return c.m()


if __name__ == "__main__":
    print("CPython:", probe())
