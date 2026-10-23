r"""G29 T3 — CHAINED store `self.x = self.y = k` in `__init__`."""
_ = 0  # anchor


class C:
    def __init__(self, k: int) -> None:
        self.x = self.y = k


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    c = C(5)
    return c.x


if __name__ == "__main__":
    print("CPython:", probe())
